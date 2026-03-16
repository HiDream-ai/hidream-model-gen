#!/usr/bin/env python3
"""
调试 angel_wings - 测试 GET 方法
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
    "X-accept-language": "en"
}

print("="*60)
print("调试 angel_wings - 测试 GET 方法")
print("="*60)

# 使用已知会失败的 task_id
task_id = "25464162-0cda-4299-96ea-95cb9851d6c7"

result_url = f"{BASE_URL}/v3/video/video_diffusion_img2vid/async/results?task_id={task_id}"
print(f"\n📤 查询任务 (GET): {task_id}")
print(f"URL: {result_url}")

try:
    result_resp = requests.get(result_url, headers=headers, timeout=30)
    print(f"\n📥 状态码: {result_resp.status_code}")
    print(f"📥 原始响应: {result_resp.text[:500]}")
    
    if result_resp.status_code == 200:
        try:
            data = result_resp.json()
            print(f"\n✅ 成功!")
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"\n⚠️  JSON解析错误: {e}")
    elif result_resp.status_code == 404:
        print("\n❌ 404: 任务不存在或已被删除")
    else:
        print(f"\n❌ 错误: {result_resp.status_code}")
except Exception as e:
    print(f"\n❌ 请求失败: {e}")

print("\n" + "="*60)
