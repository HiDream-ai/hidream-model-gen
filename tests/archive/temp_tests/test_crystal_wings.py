#!/usr/bin/env python3
"""
测试 crystal_wings (之前通过的模板)
"""
import sys
import os

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from vivago_client import create_client

print("="*60)
print("测试 crystal_wings (之前通过的模板)")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='crystal_wings',
        wh_ratio='9:16'
    )
    if result and result[0].get('video'):
        print(f"✅ 成功: {result[0].get('video')}")
    else:
        print(f"❌ 失败或无视频: {result}")
except Exception as e:
    print(f"❌ 错误: {e}")

print("="*60)
