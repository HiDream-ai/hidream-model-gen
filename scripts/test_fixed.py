#!/usr/bin/env python3
"""
修复后的模板测试脚本 - 正确解析结果类型（增加超时）
"""

import sys
sys.path.insert(0, '.')

from vivago_client import create_client
from template_manager import get_template_manager
import requests
import json
import time

# 增加全局超时
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

client = create_client()
manager = get_template_manager()
image_uuid = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'

# 创建带重试的 session
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

def test_template_with_result(template_id):
    """测试模板并正确获取结果"""
    template = manager.get_template(template_id)
    name = template.get('display_name', template_id)
    
    print(f"\n测试: {name} ({template_id})")
    print('-' * 50)
    
    # 提交任务
    submit_url = f"{client.base_url}{template['endpoint']}"
    headers_post = {**client.headers, 'Content-Type': 'application/json'}
    
    data = manager.build_request_data(template_id, image_uuid, wh_ratio='9:16')
    
    print("1. 提交任务...", end=' ', flush=True)
    try:
        resp = session.post(submit_url, json=data, headers=headers_post, timeout=60)
        result = resp.json()
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None
    
    if result.get('code') != 0:
        msg = result.get('message', '未知错误')
        print(f"❌ 失败: {msg}")
        return None
    
    task_id = result.get('result', {}).get('task_id')
    print(f"✅ TaskID: {task_id[:8]}...")
    
    # 轮询结果
    result_endpoint = template.get('result_endpoint')
    poll_url = f"{client.base_url}{result_endpoint}?task_id={task_id}"
    
    print("2. 轮询结果...")
    max_attempts = 60
    
    for attempt in range(max_attempts):
        time.sleep(6)
        
        try:
            poll_resp = session.get(poll_url, headers=client.headers, timeout=30)
            poll_data = poll_resp.json()
        except Exception as e:
            print(f"   ⚠️ 查询异常: {e}")
            continue
        
        if poll_data.get('code') != 0:
            msg = poll_data.get('message', '未知错误')
            print(f"   ❌ 查询失败: {msg}")
            return None
        
        result_info = poll_data.get('result', {})
        sub_results = result_info.get('sub_task_results', [])
        
        if sub_results:
            if all(r.get('task_status') in {1, 3, 4} for r in sub_results):
                task_info = sub_results[0]
                status = task_info.get('task_status')
                
                if status == 1:
                    result_data = task_info.get('result', {})
                    
                    if result_data.get('image'):
                        img_url = result_data['image']
                        print(f"   ✅ 🖼️ 图片结果")
                        print(f"      URL: {img_url[:50]}...")
                        return {'status': 'success', 'type': 'image', 'url': img_url}
                    elif result_data.get('video'):
                        vid_url = result_data['video']
                        print(f"   ✅ 🎬 视频结果")
                        print(f"      URL: {vid_url[:50]}...")
                        return {'status': 'success', 'type': 'video', 'url': vid_url}
                    else:
                        print(f"   ✅ 完成，但无 image/video 字段")
                        keys = list(result_data.keys()) if result_data else []
                        print(f"      可用字段: {keys}")
                        return {'status': 'success', 'type': 'unknown', 'data': result_data}
                        
                elif status == 3:
                    print(f"   ❌ 任务失败")
                    return {'status': 'failed'}
                elif status == 4:
                    print(f"   🚫 敏感内容违规")
                    return {'status': 'rejected'}
        
        if attempt % 5 == 0:
            queue_count = result_info.get('queue_count', 0)
            print(f"   ⏳ 处理中... (尝试 {attempt+1}/{max_attempts}, 队列: {queue_count})")
    
    print(f"   ⏱️ 超时")
    return {'status': 'timeout', 'task_id': task_id}

# 测试 motorcycle_boy
print('=' * 60)
print('修复后的测试 - 正确解析结果类型')
print('=' * 60)

result = test_template_with_result('motorcycle_boy')

print('\n' + '=' * 60)
if result:
    print(f"测试结果: {result}")
else:
    print('测试失败')
print('=' * 60)
