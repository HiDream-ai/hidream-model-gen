#!/usr/bin/env python3
"""
单独测试 1970s 模板 - 修复版
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

from scripts.template_manager import get_template_manager
import requests
import json
import time
import urllib3
from datetime import datetime

# 禁用 SSL 警告（仅用于测试）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置
TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiIyODg4Njc1NS0xOTA2LTRiY2YtODgzNC04MDFlNDM4OTliYWIiLCJ1c2VybmFtZSI6ImRpc2NvcmRfcUR6SVJvYiIsInBob25lbnVtIjoiMTIzNDU2Nzg5MTAiLCJlbWFpbCI6InpoYW9mYW5xaXVAZ21haWwuY29tIiwicm9sZSI6ImFwaSZlLWNvbW1lcmNlciZnZW5lcmFsIiwiZXhwIjo0ODY0ODc2MzM5fQ.pstbKg6H9I6KFG5fTPgpzkkrV6hd5YYoe0PbHV2YIYk"
BASE_URL = "https://vivago.ai/api/gw"
MAX_WAIT_TIME = 300
POLL_INTERVAL = 10

manager = get_template_manager()

def make_request(method, url, **kwargs):
    """统一请求方法，带超时和重试"""
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f'Bearer {TOKEN}'
    headers['X-accept-language'] = 'en'
    
    # 使用 Session 并配置连接池
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=1,
        pool_maxsize=1,
        max_retries=urllib3.Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
    )
    session.mount('https://', adapter)
    
    try:
        response = session.request(
            method, 
            url, 
            headers=headers, 
            timeout=(10, 120),  # (连接超时, 读取超时)
            **kwargs
        )
        return response
    finally:
        session.close()

def poll_task_result(task_id, result_endpoint):
    """轮询任务结果"""
    url = f"{BASE_URL}{result_endpoint}?task_id={task_id}"
    
    print(f"  轮询URL: {url}")
    
    start_time = time.time()
    attempt = 0
    while time.time() - start_time < MAX_WAIT_TIME:
        attempt += 1
        try:
            resp = make_request('GET', url)
            print(f"  轮询 #{attempt}: HTTP {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"    响应: {resp.text[:200]}")
                time.sleep(POLL_INTERVAL)
                continue
            
            result = resp.json()
            print(f"    响应code: {result.get('code')}")
            
            if result.get('code') == 0:
                result_data = result.get('result', {})
                
                # 首先检查 sub_task_results
                sub_results = result_data.get('sub_task_results', []) if isinstance(result_data, dict) else []
                if sub_results and len(sub_results) > 0:
                    task_info = sub_results[0]
                    status = task_info.get('task_status', 0)
                    print(f"    从sub_task_results获取, task_status: {status}")
                elif isinstance(result_data, dict) and 'task_status' in result_data:
                    task_info = result_data
                    status = task_info.get('task_status', 0)
                    print(f"    从result直接获取, task_status: {status}")
                elif isinstance(result_data, list) and len(result_data) > 0:
                    task_info = result_data[0]
                    status = task_info.get('task_status', 0)
                    print(f"    从result列表获取, task_status: {status}")
                else:
                    print(f"    result_data内容: {result_data}")
                    status = 0
                
                if status == 1:
                    return {'status': 'completed', 'data': task_info}
                elif status == 3:
                    return {'status': 'failed', 'error': 'Task failed'}
                elif status == 4:
                    return {'status': 'rejected', 'error': 'Content rejected'}
            
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"  轮询错误: {type(e).__name__}: {e}")
            time.sleep(POLL_INTERVAL)
    
    return {'status': 'timeout', 'error': 'Max wait time exceeded'}

def main():
    template_id = '1970s'
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
    
    # 构建请求数据
    print("\n1. 准备请求数据...")
    try:
        data = manager.build_request_data(template_id, TEST_IMAGE_UUID, wh_ratio=wh_ratio)
        url = f"{BASE_URL}{template['endpoint']}"
        
        print(f"   POST {url}")
        print(f"   请求体: {json.dumps(data, indent=2)[:800]}...")
    except Exception as e:
        print(f"❌ 构建请求数据失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 提交任务（带重试）
    print("\n2. 提交任务...")
    max_submit_retries = 3
    task_id = None
    
    for submit_attempt in range(max_submit_retries):
        try:
            print(f"   尝试 {submit_attempt + 1}/{max_submit_retries}...")
            
            resp = make_request('POST', url, json=data, headers={'Content-Type': 'application/json'})
            result = resp.json()
            
            print(f"   响应: {json.dumps(result, indent=2)[:600]}")
            
            if result.get('code') != 0:
                print(f"❌ 提交失败: {result.get('message', 'Unknown error')}")
                if submit_attempt < max_submit_retries - 1:
                    print("   3秒后重试...")
                    time.sleep(3)
                    continue
                return
            
            task_id = result.get('result', {}).get('task_id')
            print(f"✅ 提交成功! TaskID: {task_id}")
            break
            
        except requests.exceptions.Timeout as e:
            print(f"❌ 提交超时: {e}")
            if submit_attempt < max_submit_retries - 1:
                print("   3秒后重试...")
                time.sleep(3)
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
    print(f"\n3. 轮询结果 (最多等待{MAX_WAIT_TIME//60}分钟)...")
    poll_result = poll_task_result(task_id, template['result_endpoint'])
    
    # 输出结果
    print(f"\n4. 最终结果:")
    if poll_result['status'] == 'completed':
        task_data = poll_result['data']
        print(f"   ✅ 成功!")
        print(f"   视频: {task_data.get('video', 'N/A')}")
        print(f"   图片: {task_data.get('image', 'N/A')}")
    elif poll_result['status'] == 'rejected':
        print(f"   🚫 敏感内容违规")
    elif poll_result['status'] == 'failed':
        print(f"   ❌ 任务失败")
    else:
        print(f"   ⏱️ 超时")

if __name__ == '__main__':
    main()
