#!/usr/bin/env python3
"""
验证 metallic_liquid 修复
测试使用正确名称 'metallic_liquid'
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
print("验证 metallic_liquid 修复")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

print(f"\n🎭 测试模板名称: metallic_liquid")
print(f"⏳ 生成中...")

try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='metallic_liquid',  # 使用修复后的正确名称
        wh_ratio='1:1'
    )
    
    if result and len(result) > 0:
        video_id = result[0].get('video', 'N/A')
        print(f"\n✅ 成功!")
        print(f"   视频ID: {video_id}")
        print("\n" + "="*60)
        print("✅ 修复验证通过! metallic_liquid 正常工作")
        print("="*60)
    else:
        print(f"\n❌ 失败: 无结果")
except Exception as e:
    print(f"\n❌ 错误: {e}")
