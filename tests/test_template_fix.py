#!/usr/bin/env python3
"""
验证模板修复
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
print("验证模板修复 - ghibli")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

print("\n🎭 测试 ghibli 模板...")
print("⏳ 生成中...")

try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='ghibli',
        wh_ratio='9:16'
    )
    
    if result and len(result) > 0:
        print(f"\n✅ 成功!")
        print(f"   结果: {result}")
    else:
        print(f"\n⚠️  无结果返回")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
