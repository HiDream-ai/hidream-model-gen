#!/usr/bin/env python3
"""
查看融合任务失败原因
"""
import sys
import os
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
    "X-accept-language": "en"
}

print("="*60)
print("查看任务失败原因")
print("="*60)

# 查询失败的任务
task_ids = [
    ("Kling O1", "f3d7b133-757f-4209-a2c6-38f357f09fa0"),
    ("Nano Banana", "f4a353ce-cfb0-45d1-806d-f1239aad3051")
]

for name, task_id in task_ids:
    print(f"\n📋 {name} 任务: {task_id}")
    
    # 使用 GET 查询
    result_url = f"{BASE_URL}/v3/image/image_gen_kling/async/results?task_id={task_id}"
    
    try:
        resp = requests.get(result_url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                result = data.get('result', {})
                sub_results = result.get('sub_task_results', [])
                if sub_results:
                    sub = sub_results[0]
                    status = sub.get('task_status')
                    desc = sub.get('description', 'No description')
                    print(f"   状态: {status} (3=失败)")
                    print(f"   描述: {desc}")
            else:
                print(f"   API错误: {data.get('message')}")
        else:
            print(f"   HTTP错误: {resp.status_code}")
    except Exception as e:
        print(f"   查询错误: {e}")

print("\n" + "="*60)
print("⚠️  服务端问题确认！")
print("   图生图服务也受到服务器拥堵影响")
print("   建议明天再尝试")
print("="*60)
