#!/usr/bin/env python3
"""
对比测试: angel_wings vs phoenix_wings
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
print("对比测试: angel_wings vs phoenix_wings")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

# 测试 phoenix_wings (已知正常)
print("\n🎭 测试 phoenix_wings (已知正常)...")
try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='phoenix_wings',
        wh_ratio='9:16'
    )
    if result:
        print(f"✅ phoenix_wings 成功: {result[0].get('video')}")
    else:
        print("❌ phoenix_wings 失败")
except Exception as e:
    print(f"❌ phoenix_wings 错误: {e}")

# 测试 angel_wings
print("\n🎭 测试 angel_wings (问题模板)...")
try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='angel_wings',
        wh_ratio='9:16'
    )
    if result:
        print(f"✅ angel_wings 成功: {result[0].get('video')}")
    else:
        print("❌ angel_wings 失败")
except Exception as e:
    print(f"❌ angel_wings 错误: {e}")

print("\n" + "="*60)
