#!/usr/bin/env python3
"""
调试 angel_wings 模板 - 查看原始响应
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
print("调试 angel_wings - 查询结果端点")
print("="*60)

# 使用已知会失败的 task_id
task_id = "25464162-0cda-4299-96ea-95cb9851d6c7"

result_url = f"{BASE_URL}/v3/video/video_diffusion_img2vid/async/results"
print(f"\n📤 查询任务: {task_id}")
print(f"URL: {result_url}")

try:
    result_resp = requests.post(
        result_url,
        headers=headers,
        json={"task_id": task_id},
        timeout=30
    )
    print(f"\n📥 状态码: {result_resp.status_code}")
    print(f"📥 响应头: {dict(result_resp.headers)}")
    print(f"📥 原始响应: {result_resp.text[:500]}")
    
    # 检查是否是 404
    if result_resp.status_code == 404:
        print("\n❌ 确认: 服务端返回 404")
        print("   任务可能已被删除或从未存在")
    elif result_resp.text:
        try:
            data = result_resp.json()
            print(f"\n📥 JSON响应:")
            print(json.dumps(data, indent=2))
        except:
            print(f"\n⚠️  响应不是JSON: {result_resp.text[:200]}")
except Exception as e:
    print(f"\n❌ 请求失败: {e}")

print("\n" + "="*60)
