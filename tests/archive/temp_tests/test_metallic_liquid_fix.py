#!/usr/bin/env python3
"""
测试 metallic_liquid_ 模板（正确名称）
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
print("测试 metallic_liquid_ 模板")
print("注意：模板名称带下划线")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

print(f"\n🎭 金属液体 (metallic_liquid_) - 30积分")
print("   ⏳ 生成中...")

try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='metallic_liquid_',  # 正确的名称（带下划线）
        wh_ratio='1:1'
    )
    
    if result and len(result) > 0:
        video_id = result[0].get('video', 'N/A')
        print(f"   ✅ 成功!")
        print(f"      视频ID: {video_id}")
        print("\n" + "="*60)
        print("✅ 测试通过!")
        print("="*60)
        print("\n问题原因：模板名称是 'metallic_liquid_'（带下划线）")
        print("而不是 'metallic_liquid'")
    else:
        print(f"   ❌ 失败: 无结果")
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()
