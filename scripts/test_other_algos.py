#!/usr/bin/env python3
"""
测试其他 algo_type 模板是否需要 create_submit
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://vivago.ai/api/gw"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiIyODg4Njc1NS0xOTA2LTRiY2YtODgzNC04MDFlNDM4OTliYWIiLCJ1c2VybmFtZSI6ImRpc2NvcmRfcUR6SVJvYiIsInBob25lbnVtIjoiMTIzNDU2Nzg5MTAiLCJlbWFpbCI6InpoYW9mYW5xaXVAZ21haWwuY29tIiwicm9sZSI6ImFwaSZlLWNvbW1lcmNlciZnZW5lcmFsIiwiZXhwIjo0ODY0ODc2MzM5fQ.pstbKg6H9I6KFG5fTPgpzkkrV6hd5YYoe0PbHV2YIYk"
IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'X-accept-language': 'en',
    'Content-Type': 'application/json'
}

print("="*60)
print("测试其他 algo_type 模板")
print("="*60)

from template_manager import get_template_manager
manager = get_template_manager()

# 测试 couple_kissing (outfit_transformer)
test_cases = [
    ('couple_kissing', 'outfit_transformer'),
    ('hold_deceased', 'outfit_transformer'),
    ('photo_restore', 'figure_transformer'),
]

for template_id, expected_algo in test_cases:
    print(f"\n{'='*60}")
    print(f"测试: {template_id} ({expected_algo})")
    print(f"{'='*60}")
    
    template = manager.get_template(template_id)
    if not template:
        print(f"  ❌ 模板不存在")
        continue
    
    print(f"  algo_type: {template.get('algo_type')}")
    print(f"  endpoint: {template.get('endpoint')}")
    
    # 构建请求
    data = manager.build_request_data(template_id, IMAGE_UUID, wh_ratio='1:1')
    
    print(f"  create_submit 存在: {'create_submit' in data}")
    
    # 发送请求
    url = f"{BASE_URL}{template.get('endpoint')}"
    print(f"\n  发送请求...")
    print(f"  开始: {datetime.now().isoformat()}")
    
    start = time.time()
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        elapsed = time.time() - start
        print(f"  响应时间: {elapsed:.2f}秒")
        print(f"  HTTP: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"  API Code: {result.get('code')}")
            print(f"  API Message: {result.get('message')}")
            
            if result.get('code') == 0:
                task_id = result.get('result', {}).get('task_id')
                print(f"  ✅ 成功! TaskID: {task_id}")
            else:
                print(f"  ❌ API 错误: {result.get('message')}")
        else:
            print(f"  ❌ HTTP 错误: {resp.text[:100]}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"  ❌ 超时 ({elapsed:.2f}秒)")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ 错误: {type(e).__name__}: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
