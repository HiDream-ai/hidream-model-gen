#!/usr/bin/env python3
"""
调试 angel_wings 模板 404 问题
"""
import sys
import os
import json
import requests

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
print("调试 angel_wings 模板 404 问题")
print("="*60)

from template_manager import get_template_manager
tm = get_template_manager()
template = tm.get_template('angel_wings')

print(f"\n📋 模板信息:")
print(f"  名称: {template['name']}")
print(f"  UUID: {template['uuid']}")
print(f"  端点: {template['endpoint']}")
print(f"  回调: {template['result_endpoint']}")
print(f"  模块: {template['module']}")
print(f"  版本: {template['version']}")

# 尝试直接调用 API
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

request_data = {
    "module": template['module'],
    "version": template['version'],
    "prompt": "",
    "images": [image_uuid],
    "masks": [],
    "videos": [],
    "audios": [],
    "params": {
        "mode": "Slow",
        "style": "default",
        "height": -1,
        "width": -1,
        "seed": -1,
        "duration": 5,
        "motion": 0,
        "x": 0,
        "y": 0,
        "z": 0,
        "reserved_str": "",
        "batch_size": 1,
        "wh_ratio": "9:16",
        "custom_params": template.get('custom_params', {})
    },
    "template_id": template['template_id']
}

print(f"\n📤 提交请求...")
url = f"{BASE_URL}{template['endpoint']}"
print(f"URL: {url}")
print(f"请求体: {json.dumps(request_data, indent=2)[:500]}...")

try:
    resp = requests.post(url, headers=headers, json=request_data, timeout=30)
    result = resp.json()
    print(f"\n📥 响应:")
    print(json.dumps(result, indent=2))
    
    if result.get('code') == 0:
        task_id = result.get('data', {}).get('task_id')
        print(f"\n✅ 任务提交成功: {task_id}")
        
        # 等待并查询结果
        import time
        print(f"\n⏳ 等待10秒后查询结果...")
        time.sleep(10)
        
        result_url = f"{BASE_URL}{template['result_endpoint']}"
        result_resp = requests.post(
            result_url,
            headers=headers,
            json={"task_id": task_id},
            timeout=30
        )
        result_data = result_resp.json()
        print(f"\n📥 查询结果:")
        print(json.dumps(result_data, indent=2))
    else:
        print(f"\n❌ 提交失败: {result.get('message')}")
except Exception as e:
    print(f"\n❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
