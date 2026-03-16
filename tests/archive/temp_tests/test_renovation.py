#!/usr/bin/env python3
"""
单独测试 renovation_of_old_photos 模板
老照片修复上色功能
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
print("测试 renovation_of_old_photos 模板")
print("老照片修复上色功能")
print("预估积分: 30")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"
print(f"✅ 使用测试图片: {image_uuid}")

print("\n🎭 老照片修复 (renovation_of_old_photos) - 30积分")
print("   ⏳ 生成中...")

try:
    # 使用 api_ports.json 中配置的端口
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='renovation_of_old_photos',  # 正确的名称
        wh_ratio='4:3'
    )
    
    if result and len(result) > 0:
        video_id = result[0].get('video', 'N/A')
        print(f"   ✅ 老照片修复成功!")
        print(f"      视频ID: {video_id}")
        print("\n" + "="*60)
        print("✅ 测试通过!")
        print("="*60)
    else:
        print(f"   ❌ 失败: 无结果")
        print("\n" + "="*60)
        print("❌ 测试失败")
        print("="*60)
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    print("❌ 测试失败")
    print("="*60)
