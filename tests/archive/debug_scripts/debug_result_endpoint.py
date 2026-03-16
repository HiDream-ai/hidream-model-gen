#!/usr/bin/env python3
"""
验证模板回调路径
"""
import sys
import os
import json
import requests
import time

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

TOKEN = os.environ.get('HIDREAM_TOKEN')
BASE_URL = "https://vivago.ai/api/gw"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-accept-language": "en",
    "Content-Type": "application/json"
}

print("="*60)
print("验证模板回调路径")
print("="*60)

# 任务ID来自之前的成功提交
task_id = "0a67aa63-4cbf-4199-b4a4-1e9d46629503"

# 尝试不同的回调路径
result_endpoints = [
    "/v3/pipeline/style_transformer/async/results",
    "/v3/video/video_diffusion/async/results",
    "/v3/video/video_diffusion_template/async/results",
]

print(f"\n任务ID: {task_id}")
print("\n测试回调路径:")

for endpoint in result_endpoints:
    url = f"{BASE_URL}{endpoint}?task_id={task_id}"
    print(f"\n尝试: {endpoint}")
    
    try:
        resp = requests.get(url, headers={"Authorization": headers["Authorization"]}, timeout=10)
        print(f"  状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"  响应: {json.dumps(result, indent=2)[:300]}")
            
            if result.get('code') == 0:
                print(f"  ✅ 此路径正确!")
                sub_results = result.get('result', {}).get('sub_task_results', [])
                if sub_results:
                    status = sub_results[0].get('task_status')
                    print(f"  任务状态: {status}")
            else:
                print(f"  ⚠️  返回错误: {result.get('message')}")
        else:
            print(f"  ❌ HTTP {resp.status_code}")
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")

print("\n" + "="*60)
