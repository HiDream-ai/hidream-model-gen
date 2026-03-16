#!/usr/bin/env python3
"""
Phase 2: 模板可靠性测试
测试之前失败的模板，区分"模板问题" vs "网络问题"
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

from scripts.vivago_client import create_client
from scripts.template_manager import get_template_manager
import requests
import json
import time
import random
from datetime import datetime

# 配置
TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
MAX_WAIT_TIME = 600  # 10分钟超时
POLL_INTERVAL = 10

# 之前失败的模板列表
FAILED_TEMPLATES = [
    ('1970s', '之前单独测试成功过'),
    ('couple_kissing', '之前超时'),
    ('hold_deceased', '之前超时'),
    ('1940s_suit_portrait', '之前超时'),
    ('photo_restore', '之前超时'),
]

client = create_client()
manager = get_template_manager()

def poll_task_result(task_id, result_endpoint):
    """轮询任务结果"""
    url = f"{client.base_url}{result_endpoint}?task_id={task_id}"
    headers_get = dict(client.headers)
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < MAX_WAIT_TIME:
        attempt += 1
        elapsed = int(time.time() - start_time)
        
        try:
            resp = requests.get(url, headers=headers_get, timeout=10)
            
            if resp.status_code != 200:
                print(f"    轮询 #{attempt}: HTTP {resp.status_code}")
                time.sleep(POLL_INTERVAL)
                continue
            
            result = resp.json()
            
            if result.get('code') == 0:
                result_data = result.get('result', {})
                
                # 检查 sub_task_results
                sub_results = result_data.get('sub_task_results', []) if isinstance(result_data, dict) else []
                if sub_results and len(sub_results) > 0:
                    task_info = sub_results[0]
                    status = task_info.get('task_status', 0)
                elif isinstance(result_data, dict) and 'task_status' in result_data:
                    task_info = result_data
                    status = task_info.get('task_status', 0)
                else:
                    status = 0
                
                status_text = {0: '等待', 1: '完成', 2: '处理中', 3: '失败', 4: '违规'}.get(status, f'未知({status})')
                
                if status == 2 and attempt % 6 == 0:  # 每60秒报告一次处理中状态
                    print(f"    轮询 #{attempt}: {status_text} ({elapsed}s)")
                
                if status == 1:
                    return {'status': 'completed', 'data': task_info}
                elif status == 3:
                    return {'status': 'failed', 'error': 'Task failed'}
                elif status == 4:
                    return {'status': 'rejected', 'error': 'Content rejected'}
            
            time.sleep(POLL_INTERVAL)
            
        except requests.exceptions.Timeout:
            print(f"    轮询 #{attempt}: 超时")
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"    轮询 #{attempt}: 错误 {type(e).__name__}")
            time.sleep(POLL_INTERVAL)
    
    return {'status': 'timeout', 'error': f'Max wait time exceeded ({MAX_WAIT_TIME//60} minutes)'}

def test_template(template_id, previous_status):
    """测试单个模板"""
    template = manager.get_template(template_id)
    if not template:
        return {'success': False, 'error': 'Template not found', 'type': 'template_issue'}
    
    print(f"\n{'='*60}")
    print(f"测试: {template['name']} ({template_id})")
    print(f"之前状态: {previous_status}")
    print(f"算法: {template.get('algo_type')}")
    print(f"{'='*60}")
    
    # 随机选择比例
    supported = template.get('supported_ratios', ['1:1'])
    wh_ratio = random.choice(supported)
    print(f"使用比例: {wh_ratio}")
    
    # 1. 提交任务
    print("\n1. 提交任务...", end=' ', flush=True)
    submit_time = datetime.now()
    
    try:
        data = manager.build_request_data(template_id, TEST_IMAGE_UUID, wh_ratio=wh_ratio)
        url = f"{client.base_url}{template['endpoint']}"
        headers_post = {**client.headers, 'Content-Type': 'application/json'}
        
        resp = requests.post(url, json=data, headers=headers_post, timeout=20)
        result = resp.json()
        
        if result.get('code') != 0:
            error_msg = result.get('message', 'Unknown error')
            print(f"❌ 失败")
            print(f"   错误: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'type': 'api_error',
                'stage': 'submit'
            }
        
        task_id = result.get('result', {}).get('task_id')
        print(f"✅ TaskID: {task_id[:8]}...")
        
    except requests.exceptions.Timeout:
        print(f"❌ 超时")
        return {
            'success': False,
            'error': 'Submit timeout',
            'type': 'network_issue',
            'stage': 'submit'
        }
    except Exception as e:
        print(f"❌ 异常: {e}")
        return {
            'success': False,
            'error': str(e),
            'type': 'network_issue',
            'stage': 'submit'
        }
    
    # 2. 轮询结果
    print(f"2. 轮询结果 (最多{MAX_WAIT_TIME//60}分钟)...")
    result_endpoint = template.get('result_endpoint', '/v3/video/video_diffusion/async/results')
    poll_result = poll_task_result(task_id, result_endpoint)
    
    complete_time = datetime.now()
    duration = (complete_time - submit_time).total_seconds()
    
    # 3. 分析结果
    print(f"\n3. 结果分析:")
    
    if poll_result['status'] == 'completed':
        task_data = poll_result['data']
        video_id = task_data.get('video', 'N/A')
        print(f"   ✅ 成功! 耗时: {duration:.1f}秒")
        print(f"   视频ID: {video_id[:30]}..." if video_id != 'N/A' else "   视频ID: N/A")
        return {
            'success': True,
            'duration': duration,
            'type': 'success',
            'video_id': video_id
        }
    elif poll_result['status'] == 'rejected':
        print(f"   🚫 敏感内容违规")
        return {
            'success': False,
            'error': 'Content rejected',
            'type': 'template_issue',
            'stage': 'processing'
        }
    elif poll_result['status'] == 'failed':
        print(f"   ❌ 任务失败")
        return {
            'success': False,
            'error': 'Task processing failed',
            'type': 'template_issue',
            'stage': 'processing'
        }
    else:  # timeout
        print(f"   ⏱️ 超时 (>{MAX_WAIT_TIME//60}分钟)")
        return {
            'success': False,
            'error': 'Timeout',
            'type': 'network_issue',
            'stage': 'polling',
            'duration': duration
        }

def main():
    """主函数"""
    print("\n" + "="*60)
    print("Phase 2: 模板可靠性测试")
    print("="*60)
    print(f"测试时间: {datetime.now().isoformat()}")
    print(f"测试图片: {TEST_IMAGE_UUID}")
    print(f"模板数量: {len(FAILED_TEMPLATES)}")
    print(f"每个模板最大等待: {MAX_WAIT_TIME//60}分钟")
    print("="*60)
    
    results = {}
    stats = {
        'success': 0,
        'template_issue': 0,
        'network_issue': 0,
        'api_error': 0
    }
    
    for i, (template_id, previous_status) in enumerate(FAILED_TEMPLATES, 1):
        print(f"\n\n{'#'*60}")
        print(f"# 进度: {i}/{len(FAILED_TEMPLATES)} ({i*100//len(FAILED_TEMPLATES)}%)")
        print(f"{'#'*60}")
        
        result = test_template(template_id, previous_status)
        results[template_id] = result
        
        # 统计
        if result['success']:
            stats['success'] += 1
        else:
            issue_type = result.get('type', 'unknown')
            stats[issue_type] = stats.get(issue_type, 0) + 1
        
        # 显示统计
        print(f"\n📊 当前统计:")
        print(f"   ✅ 成功: {stats['success']}")
        print(f"   🔧 模板问题: {stats.get('template_issue', 0)}")
        print(f"   🌐 网络问题: {stats.get('network_issue', 0)}")
        print(f"   ⚠️  API错误: {stats.get('api_error', 0)}")
    
    # 保存结果
    with open('phase2_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'test_time': datetime.now().isoformat(),
            'templates': results,
            'stats': stats
        }, f, indent=2, ensure_ascii=False)
    
    # 最终报告
    print(f"\n\n{'='*60}")
    print("Phase 2 测试完成!")
    print(f"{'='*60}")
    print(f"✅ 成功: {stats['success']}")
    print(f"🔧 模板问题: {stats.get('template_issue', 0)}")
    print(f"🌐 网络问题: {stats.get('network_issue', 0)}")
    print(f"⚠️  API错误: {stats.get('api_error', 0)}")
    
    print(f"\n详细结果:")
    for tid, result in results.items():
        status = "✅" if result['success'] else "❌"
        issue_type = result.get('type', 'unknown')
        print(f"  {status} {tid}: {issue_type}")
    
    print(f"\n结果已保存到: phase2_test_results.json")
    print("="*60)

if __name__ == '__main__':
    main()
