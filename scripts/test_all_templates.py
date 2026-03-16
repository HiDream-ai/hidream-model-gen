#!/usr/bin/env python3
"""
严格串行模板测试脚本
- 逐个测试，一个完成再下一个
- 验证最终结果（不只是提交）
- 区分视频/图片结果类型
- 更新测试报告到 TEMPLATE_TEST_REPORT.md
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

from scripts.vivago_client import create_client
from scripts.template_manager import get_template_manager
import requests
import json
import time
from datetime import datetime

# 配置
TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
MAX_WAIT_TIME = 300  # 最大等待5分钟
POLL_INTERVAL = 10   # 每10秒轮询一次

client = create_client()
manager = get_template_manager()

# 混合测试：2个通过 + 3个超时
TEST_TEMPLATES = [
    '1960s',           # 之前通过
    'animal_and_turkey',  # 之前通过
    '1970s',           # 之前超时（但单独测试成功过）
    'couple_kissing',  # 之前超时
    'hold_deceased',   # 之前超时
]

def poll_task_result(task_id, result_endpoint):
    """轮询任务结果，直到完成或超时"""
    # 使用 GET 请求查询结果
    url = f"{client.base_url}{result_endpoint}?task_id={task_id}"
    headers_get = client.headers
    
    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        try:
            resp = requests.get(url, headers=headers_get, timeout=10)
            result = resp.json()
            
            if result.get('code') == 0:
                result_data = result.get('result', {})
                
                # 首先检查 sub_task_results (Vivago API 标准响应格式)
                sub_results = result_data.get('sub_task_results', []) if isinstance(result_data, dict) else []
                if sub_results and len(sub_results) > 0:
                    task_info = sub_results[0]
                    status = task_info.get('task_status', 0)
                # 兼容处理：直接检查 result 是否为任务信息
                elif isinstance(result_data, dict) and 'task_status' in result_data:
                    task_info = result_data
                    status = task_info.get('task_status', 0)
                elif isinstance(result_data, list) and len(result_data) > 0:
                    task_info = result_data[0]
                    status = task_info.get('task_status', 0)
                else:
                    status = 0
                
                # 状态: 0=等待, 1=完成, 2=处理中, 3=失败, 4=被拒绝
                if status == 1:
                    return {'status': 'completed', 'data': task_info}
                elif status == 3:
                    return {'status': 'failed', 'error': 'Task failed'}
                elif status == 4:
                    return {'status': 'rejected', 'error': 'Content rejected'}
            
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"  轮询错误: {e}")
            time.sleep(POLL_INTERVAL)
    
    return {'status': 'timeout', 'error': 'Max wait time exceeded'}

def determine_result_type(task_data):
    """判断结果类型是视频还是图片"""
    # 检查是否有视频URL
    if task_data.get('video'):
        return 'video'
    # 检查是否有图片URL
    if task_data.get('image'):
        return 'image'
    # 检查其他可能的字段
    if 'video' in str(task_data).lower():
        return 'video'
    if 'image' in str(task_data).lower() or 'img' in str(task_data).lower():
        return 'image'
    return 'unknown'

def test_single_template(template_id):
    """测试单个模板，严格串行"""
    template = manager.get_template(template_id)
    if not template:
        return {'success': False, 'error': 'Template not found', 'result_type': 'unknown'}
    
    name = template.get('display_name', template_id)
    print(f"\n{'='*60}")
    print(f"测试: {name} ({template_id})")
    print(f"算法: {template.get('algo_type')}")
    print(f"{'='*60}")
    
    # 1. 提交任务
    print("1. 提交任务...", end=' ', flush=True)
    submit_time = datetime.now().isoformat()
    
    try:
        data = manager.build_request_data(template_id, TEST_IMAGE_UUID, wh_ratio='9:16')
        url = f"{client.base_url}{template['endpoint']}"
        headers_post = {**client.headers, 'Content-Type': 'application/json'}
        
        resp = requests.post(url, json=data, headers=headers_post, timeout=20)
        result = resp.json()
        
        if result.get('code') != 0:
            error_msg = result.get('message', 'Unknown error')
            print(f"❌ 提交失败: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'submit_time': submit_time,
                'result_type': 'unknown'
            }
        
        task_id = result.get('result', {}).get('task_id')
        print(f"✅ TaskID: {task_id[:8]}...")
        
    except Exception as e:
        print(f"❌ 提交异常: {e}")
        return {
            'success': False,
            'error': str(e),
            'submit_time': submit_time,
            'result_type': 'unknown'
        }
    
    # 2. 轮询等待结果
    print(f"2. 轮询结果 (最多等待{MAX_WAIT_TIME//60}分钟)...")
    result_endpoint = template.get('result_endpoint', '/v3/video/video_diffusion/async/results')
    poll_result = poll_task_result(task_id, result_endpoint)
    
    complete_time = datetime.now().isoformat()
    
    # 3. 分析结果
    if poll_result['status'] == 'completed':
        result_type = determine_result_type(poll_result['data'])
        print(f"3. ✅ 完成! 结果类型: {result_type}")
        return {
            'success': True,
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': result_type,
            'task_id': task_id
        }
    elif poll_result['status'] == 'rejected':
        print(f"3. 🚫 敏感内容违规")
        return {
            'success': False,
            'error': 'Content rejected (sensitive)',
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': 'rejected',
            'task_id': task_id
        }
    elif poll_result['status'] == 'failed':
        print(f"3. ❌ 任务失败")
        return {
            'success': False,
            'error': 'Task processing failed',
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': 'failed',
            'task_id': task_id
        }
    else:  # timeout
        print(f"3. ⏱️ 超时")
        return {
            'success': False,
            'error': 'Timeout',
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': 'timeout',
            'task_id': task_id
        }

def update_report(test_results):
    """更新测试报告文件"""
    # 这里可以添加更新 MARKDOWN 文件的逻辑
    # 为简化，先保存JSON格式的详细结果
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 测试结果已保存到 test_results.json")

def main():
    """主函数：严格串行测试所有模板"""
    print("="*60)
    print("Vivago AI 模板严格串行测试")
    print("="*60)
    print(f"测试图片: {TEST_IMAGE_UUID}")
    print(f"模板数量: {len(TEST_TEMPLATES)}")
    print(f"测试策略: 严格串行，验证最终结果")
    print("="*60)
    
    results = {
        'test_start': datetime.now().isoformat(),
        'test_image': TEST_IMAGE_UUID,
        'templates': {}
    }
    
    stats = {'passed': 0, 'failed': 0, 'rejected': 0, 'timeout': 0, 'video': 0, 'image': 0}
    
    for i, template_id in enumerate(TEST_TEMPLATES, 1):
        print(f"\n\n{'#'*60}")
        print(f"# 进度: {i}/{len(TEST_TEMPLATES)} ({i*100//len(TEST_TEMPLATES)}%)")
        print(f"{'#'*60}")
        
        result = test_single_template(template_id)
        results['templates'][template_id] = result
        
        # 统计
        if result['success']:
            stats['passed'] += 1
            if result.get('result_type') == 'video':
                stats['video'] += 1
            elif result.get('result_type') == 'image':
                stats['image'] += 1
        else:
            if result.get('result_type') == 'rejected':
                stats['rejected'] += 1
            elif result.get('result_type') == 'timeout':
                stats['timeout'] += 1
            else:
                stats['failed'] += 1
        
        # 显示统计
        print(f"\n📊 当前统计:")
        print(f"   ✅ 通过: {stats['passed']} (🎬视频:{stats['video']} 🖼️图片:{stats['image']})")
        print(f"   ❌ 失败: {stats['failed']}")
        print(f"   🚫 违规: {stats['rejected']}")
        print(f"   ⏱️ 超时: {stats['timeout']}")
    
    results['test_end'] = datetime.now().isoformat()
    results['stats'] = stats
    
    # 保存结果
    update_report(results)
    
    # 最终报告
    print(f"\n\n{'='*60}")
    print("测试完成!")
    print(f"{'='*60}")
    print(f"✅ 通过: {stats['passed']}")
    print(f"   - 视频结果: {stats['video']}")
    print(f"   - 图片结果: {stats['image']}")
    print(f"❌ 失败: {stats['failed']}")
    print(f"🚫 违规: {stats['rejected']}")
    print(f"⏱️ 超时: {stats['timeout']}")

if __name__ == '__main__':
    main()
