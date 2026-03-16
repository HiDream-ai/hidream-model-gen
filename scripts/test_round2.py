#!/usr/bin/env python3
"""
第二轮模板测试 - 10个随机模板
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

from scripts.vivago_client import create_client
from scripts.template_manager import get_template_manager
import requests
import json
import time
import random
from datetime import datetime

# 配置
TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
MAX_WAIT_TIME = 300  # 最大等待5分钟
POLL_INTERVAL = 10   # 每10秒轮询一次

# 第二轮测试的10个随机模板
TEST_TEMPLATES = [
    '1970s', 'instant_sadness', '1970s_punk_animation', 'bring_comics_to_life', 
    'couple_kissing', '1940s_suit_portrait', 'hold_deceased', 'photo_restore', 
    '1960s', 'animal_and_turkey'
]

client = create_client()
manager = get_template_manager()

def poll_task_result(task_id, result_endpoint):
    """轮询任务结果，直到完成或超时"""
    url = f"{client.base_url}{result_endpoint}?task_id={task_id}"
    headers_get = client.headers
    
    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        try:
            resp = requests.get(url, headers=headers_get, timeout=10)
            result = resp.json()
            
            if result.get('code') == 0:
                results = result.get('result', [])
                if results and len(results) > 0:
                    task_info = results[0]
                    status = task_info.get('task_status', 0)
                    
                    if status == 1:
                        return {'status': 'completed', 'data': task_info}
                    elif status == 3:
                        return {'status': 'failed', 'error': 'Task failed'}
                    elif status == 4:
                        return {'status': 'rejected', 'error': 'Content rejected'}
            
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"  轮询错误: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(POLL_INTERVAL)
    
    return {'status': 'timeout', 'error': 'Max wait time exceeded'}

def determine_result_type(task_data):
    """判断结果类型是视频还是图片"""
    if task_data.get('video'):
        return 'video'
    if task_data.get('image'):
        return 'image'
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
    
    # 随机选择比例
    supported = template.get('supported_ratios', ['1:1'])
    wh_ratio = random.choice(supported)
    
    print(f"\n{'='*60}")
    print(f"测试: {name} ({template_id})")
    print(f"算法: {template.get('algo_type')}")
    print(f"比例: {wh_ratio}")
    print(f"{'='*60}")
    
    # 1. 提交任务
    print("1. 提交任务...", end=' ', flush=True)
    submit_time = datetime.now().isoformat()
    
    try:
        data = manager.build_request_data(template_id, TEST_IMAGE_UUID, wh_ratio=wh_ratio)
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
                'result_type': 'unknown',
                'wh_ratio': wh_ratio
            }
        
        task_id = result.get('result', {}).get('task_id')
        print(f"✅ TaskID: {task_id[:8]}...")
        
    except Exception as e:
        print(f"❌ 提交异常: {e}")
        return {
            'success': False,
            'error': str(e),
            'submit_time': submit_time,
            'result_type': 'unknown',
            'wh_ratio': wh_ratio
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
            'task_id': task_id,
            'wh_ratio': wh_ratio
        }
    elif poll_result['status'] == 'rejected':
        print(f"3. 🚫 敏感内容违规")
        return {
            'success': False,
            'error': 'Content rejected (sensitive)',
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': 'rejected',
            'task_id': task_id,
            'wh_ratio': wh_ratio
        }
    elif poll_result['status'] == 'failed':
        print(f"3. ❌ 任务失败")
        return {
            'success': False,
            'error': 'Task processing failed',
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': 'failed',
            'task_id': task_id,
            'wh_ratio': wh_ratio
        }
    else:  # timeout
        print(f"3. ⏱️ 超时")
        return {
            'success': False,
            'error': 'Timeout',
            'submit_time': submit_time,
            'complete_time': complete_time,
            'result_type': 'timeout',
            'task_id': task_id,
            'wh_ratio': wh_ratio
        }

def main():
    """主函数：严格串行测试所有模板"""
    print("="*60)
    print("Vivago AI 第二轮模板测试 - 10个随机模板")
    print("="*60)
    print(f"测试图片: {TEST_IMAGE_UUID}")
    print(f"模板数量: {len(TEST_TEMPLATES)}")
    print(f"测试策略: 严格串行，随机比例")
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
    with open('test_results_round2.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 测试结果已保存到 test_results_round2.json")
    
    # 最终报告
    print(f"\n\n{'='*60}")
    print("第二轮测试完成!")
    print(f"{'='*60}")
    print(f"✅ 通过: {stats['passed']}")
    print(f"   - 视频结果: {stats['video']}")
    print(f"   - 图片结果: {stats['image']}")
    print(f"❌ 失败: {stats['failed']}")
    print(f"🚫 违规: {stats['rejected']}")
    print(f"⏱️ 超时: {stats['timeout']}")
    
    # 详细结果
    print(f"\n详细结果:")
    for tid, result in results['templates'].items():
        status = "✅" if result['success'] else "❌"
        ratio = result.get('wh_ratio', 'unknown')
        print(f"  {status} {tid} ({ratio})")

if __name__ == '__main__':
    main()
