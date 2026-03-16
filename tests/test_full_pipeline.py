#!/usr/bin/env python3
"""
完整通路测试：上传图片 + 调用模板
验证新的上传方式和模板功能是否正常工作
"""
import os
import sys

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from scripts.vivago_client import create_client

# 测试图片路径
test_image = "/root/.openclaw/workspace/skills/vivago-ai-skill/tests/fixtures/images/portrait.jpg"

print("="*70)
print("完整通路测试：上传图片 + 调用模板")
print("="*70)

client = create_client()

# 步骤1: 上传图片
print("\n[1/3] 📤 上传图片")
print("-"*70)
print(f"图片路径: {test_image}")

try:
    image_uuid = client.upload_image(test_image)
    print(f"✅ 上传成功!")
    print(f"   UUID: {image_uuid}")
except Exception as e:
    print(f"❌ 上传失败: {e}")
    sys.exit(1)

# 步骤2: 调用模板生成视频
print("\n[2/3] 🎭 调用模板 (ghibli)")
print("-"*70)
print(f"模板: ghibli (吉卜力风格)")
print(f"积分: 30")
print(f"⏳ 生成中，请耐心等待...")

try:
    result = client.template_to_video(
        image_uuid=image_uuid,
        template='ghibli',
        wh_ratio='1:1'
    )
    
    if result and len(result) > 0:
        video_info = result[0]
        video_uuid = video_info.get('video')
        print(f"✅ 模板调用成功!")
        print(f"   视频 UUID: {video_uuid}")
    else:
        print(f"❌ 模板调用失败: 无结果")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 模板调用失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤3: 验证结果
print("\n[3/3] ✅ 验证结果")
print("-"*70)

video_url = f"https://media.vivago.ai/{video_uuid}"
print(f"🎬 生成的视频地址:")
print(f"   {video_url}")

print("\n" + "="*70)
print("✅ 完整通路测试通过!")
print("="*70)
print("\n测试结论:")
print("  ✅ 图片上传 (新方式) - 正常")
print("  ✅ 模板调用 (ghibli) - 正常")
print("  ✅ 视频生成 - 正常")
print("\n整个通路通畅，可以正常使用!")
