#!/usr/bin/env python3
"""
测试修复后的 1970s 模板
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
print("测试修复后的 1970s 模板")
print("="*60)
print(f"时间: {datetime.now().isoformat()}")
print()

from template_manager import get_template_manager
manager = get_template_manager()

# 使用修复后的 build_request_data
data = manager.build_request_data('1970s', IMAGE_UUID, wh_ratio='9:16')

print("【请求数据检查】")
print(f"  create_submit 存在: {'create_submit' in data}")
if 'create_submit' in data:
    cs = data['create_submit']
    print(f"    effect_name: {cs.get('effect_name')}")
    print(f"    model_name: {cs.get('model_name')}")
print()

# 发送请求
url = f"{BASE_URL}/v3/pipeline/proto_transformer/async"
print(f"【发送请求】")
print(f"  URL: {url}")
print(f"  开始: {datetime.now().isoformat()}")

start = time.time()
try:
    resp = requests.post(url, json=data, headers=headers, timeout=60)
    elapsed = time.time() - start
    print(f"  响应时间: {elapsed:.2f}秒")
    print(f"  HTTP 状态: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"  API Code: {result.get('code')}")
        print(f"  API Message: {result.get('message')}")
        
        if result.get('code') == 0:
            task_id = result.get('result', {}).get('task_id')
            print(f"\n  ✅ 成功! TaskID: {task_id}")
            print(f"\n🎉 1970s 模板修复成功！")
        else:
            print(f"\n  ❌ API 错误: {result.get('message')}")
    else:
        print(f"\n  ❌ HTTP 错误: {resp.text[:200]}")
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"\n  ❌ 超时 ({elapsed:.2f}秒)")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n  ❌ 错误: {type(e).__name__}: {e}")

print("\n" + "="*60)
