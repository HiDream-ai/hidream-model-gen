#!/usr/bin/env python3
"""
单独测试 hold_deceased 模板 - 30分钟超时
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

from scripts.template_manager import get_template_manager
import requests
import json
import time
import urllib3
from datetime import datetime

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置 - 30分钟超时
TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiIyODg4Njc1NS0xOTA2LTRiY2YtODgzNC04MDFlNDM4OTliYWIiLCJ1c2VybmFtZSI6ImRpc2NvcmRfcUR6SVJvYiIsInBob25lbnVtIjoiMTIzNDU2Nzg5MTAiLCJlbWFpbCI6InpoYW9mYW5xaXVAZ21haWwuY29tIiwicm9sZSI6ImFwaSZlLWNvbW1lcmNlciZnZW5lcmFsIiwiZXhwIjo0ODY0ODc2MzM5fQ.pstbKg6H9I6KFG5fTPgpzkkrV6hd5YYoe0PbHV2YIYk"
BASE_URL = "https://vivago.ai/api/gw"
MAX_WAIT_TIME = 1800  # 30分钟 = 1800秒
POLL_INTERVAL = 10

manager = get_template_manager()

def make_request(method, url, **kwargs):
    """统一请求方法"""
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f'Bearer {TOKEN}'
    headers['X-accept-language'] = 'en'
    
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=1,
        pool_maxsize=1,
        max_retries=urllib3.Retry(total=3, backoff_factor=1)
    )
    session.mount('https://', adapter)
    
    try:
        response = session.request(
            method, url, headers=headers, 
            timeout=(10, 120),  # 连接10秒，读取120秒
            **kwargs
        )
        return response
    finally:
        session.close()

def poll_task_result(task_id, result_endpoint):
    """轮询任务结果 - 30分钟超时"""
    url = f"{BASE_URL}{result_endpoint}?task_id={task_id}"
    
    print(f"\n轮询URL: {url}")
    print(f"最大等待时间: {MAX_WAIT_TIME//60}分钟")
    print("-" * 60)
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < MAX_WAIT_TIME:
        attempt += 1
        elapsed = int(time.time() - start_time)
        remaining = MAX_WAIT_TIME - elapsed
        
        try:
            resp = make_request('GET', url)
            
            if resp.status_code != 200:
                print(f"[{elapsed//60}m{elapsed%60}s] 轮询 #{attempt}: HTTP {resp.status_code}, 剩余{remaining//60}分钟")
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
                elif isinstance(result_data, list) and len(result_data) > 0:
                    task_info = result_data[0]
                    status = task_info.get('task_status', 0)
                else:
                    status = 0
                
                status_text = {0: '等待', 1: '完成', 2: '处理中', 3: '失败', 4: '违规'}.get(status, f'未知({status})')
                print(f"[{elapsed//60}m{elapsed%60}s] 轮询 #{attempt}: {status_text}, 剩余{remaining//60}分钟")
                
                if status == 1:
                    return {'status': 'completed', 'data': task_info}
                elif status == 3:
                    return {'status': 'failed', 'error': 'Task failed'}
                elif status == 4:
                    return {'status': 'rejected', 'error': 'Content rejected'}
            else:
                print(f"[{elapsed//60}m{elapsed%60}s] 轮询 #{attempt}: API错误 code={result.get('code')}, 剩余{remaining//60}分钟")
            
            time.sleep(POLL_INTERVAL)
            
        except requests.exceptions.Timeout:
            print(f"[{elapsed//60}m{elapsed%60}s] 轮询 #{attempt}: 超时, 剩余{remaining//60}分钟")
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"[{elapsed//60}m{elapsed%60}s] 轮询 #{attempt}: 错误 {type(e).__name__}, 剩余{remaining//60}分钟")
            time.sleep(POLL_INTERVAL)
    
    return {'status': 'timeout', 'error': f'Max wait time exceeded ({MAX_WAIT_TIME//60} minutes)'}

def main():
    template_id = 'hold_deceased'
    template = manager.get_template(template_id)
    
    print("="*60)
    print(f"单独测试: {template['name']} ({template_id})")
    print(f"算法: {template.get('algo_type')}")
    print(f"端点: {template['endpoint']}")
    print(f"结果端点: {template['result_endpoint']}")
    print("="*60)
    
    # 随机选择支持的比例
    supported = template.get('supported_ratios', ['1:1'])
    import random
    wh_ratio = random.choice(supported)
    print(f"\n使用比例: {wh_ratio}")
    
    # 提交任务
    print("\n" + "="*60)
    print("1. 提交任务")
    print("="*60)
    
    max_submit_retries = 5
    task_id = None
    
    for submit_attempt in range(max_submit_retries):
        try:
            data = manager.build_request_data(template_id, TEST_IMAGE_UUID, wh_ratio=wh_ratio)
            url = f"{BASE_URL}{template['endpoint']}"
            
            print(f"\n尝试 {submit_attempt + 1}/{max_submit_retries}: POST {url}")
            print(f"请求体: {json.dumps(data, indent=2)[:600]}...")
            
            resp = make_request('POST', url, json=data, headers={'Content-Type': 'application/json'})
            result = resp.json()
            
            print(f"\n响应: {json.dumps(result, indent=2)[:600]}")
            
            if result.get('code') != 0:
                print(f"❌ 提交失败: {result.get('message', 'Unknown error')}")
                if submit_attempt < max_submit_retries - 1:
                    wait_time = 5
                    print(f"   {wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
                return
            
            task_id = result.get('result', {}).get('task_id')
            print(f"\n✅ 提交成功!")
            print(f"   TaskID: {task_id}")
            print(f"   HistoryID: {result.get('result', {}).get('history_id')}")
            print(f"   SubTaskIDs: {result.get('result', {}).get('sub_task_ids')}")
            break
            
        except requests.exceptions.Timeout as e:
            print(f"❌ 提交超时: {e}")
            if submit_attempt < max_submit_retries - 1:
                wait_time = 5
                print(f"   {wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print("   所有重试都失败了")
                return
        except Exception as e:
            print(f"❌ 提交异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return
    
    if not task_id:
        print("❌ 未能获取 TaskID")
        return
    
    # 轮询结果
    print("\n" + "="*60)
    print("2. 轮询结果")
    print("="*60)
    
    poll_result = poll_task_result(task_id, template['result_endpoint'])
    
    # 输出最终结果
    print("\n" + "="*60)
    print("3. 最终结果")
    print("="*60)
    
    if poll_result['status'] == 'completed':
        task_data = poll_result['data']
        print(f"\n✅ 成功!")
        print(f"   视频ID: {task_data.get('video', 'N/A')}")
        print(f"   图片ID: {task_data.get('image', 'N/A')}")
        if task_data.get('video'):
            vid = task_data['video']
            if vid.startswith('v_'):
                vid = vid[2:]
            print(f"   视频URL: https://media.vivago.ai/{vid}")
    elif poll_result['status'] == 'rejected':
        print(f"\n🚫 敏感内容违规")
    elif poll_result['status'] == 'failed':
        print(f"\n❌ 任务失败")
    else:
        print(f"\n⏱️ 超时 (超过{MAX_WAIT_TIME//60}分钟)")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
