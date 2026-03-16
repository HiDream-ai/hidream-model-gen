#!/usr/bin/env python3
"""
用融合生物生成"开心奔跑"视频
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
print("🎬 融合生物 - 开心奔跑视频")
print("="*60)
print()

client = create_client()

# 融合生物图片 UUID
image_uuid = "p_801ddc07-98e7-46ad-b37d-29ca835d1924"

# 视频提示词
prompt = "A cute fusion Pokemon running happily with joy, cheerful expression, bouncy movement, full of energy, joyful bounce, playful running pose, vibrant animation"

print(f"🎨 图片: {image_uuid}")
print(f"📝 视频描述: {prompt}")
print()
print(f"⚙️  参数:")
print(f"   模型: v3L (快速)")
print(f"   时长: 5秒")
print(f"   模式: Fast")
print(f"   比例: 9:16 (竖屏)")
print()
print("⏳ 正在生成视频... (约2-5分钟)")
print()

try:
    result = client.image_to_video(
        prompt=prompt,
        image_uuid=image_uuid,
        port="v3L",
        wh_ratio="9:16",
        duration=5,
        mode="Fast"
    )
    
    if result and len(result) > 0 and result[0].get('video'):
        video_uuid = result[0].get('video')
        print("="*60)
        print("✅ 视频生成成功！")
        print(f"🎬 视频 UUID: {video_uuid}")
        print("="*60)
        print()
        print("🎉 融合生物正在开心地奔跑！")
    else:
        print("❌ 视频生成失败")
        print(f"结果: {result}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
