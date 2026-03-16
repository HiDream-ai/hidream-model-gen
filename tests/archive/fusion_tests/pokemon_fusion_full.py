#!/usr/bin/env python3
"""
重新执行：生成皮卡丘 + 四图融合
使用正确的 UUID 格式
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
print("🎨 宝可梦融合 - 重新执行")
print("="*60)
print()

client = create_client()

# 第一步：生成皮卡丘
print("🎨 第一步：生成皮卡丘...")
prompt = "Pikachu, the electric mouse Pokemon, yellow body, red cheeks, lightning tail, cute, white background, digital art, high quality"

try:
    result = client.text_to_image(
        prompt=prompt,
        port="kling-image",
        wh_ratio="1:1",
        batch_size=1
    )
    
    if result and len(result) > 0:
        pikachu_uuid = result[0].get('image', '')
        print(f"✅ 皮卡丘生成成功!")
        print(f"📷 皮卡丘 UUID: {pikachu_uuid}")
        print()
    else:
        print("❌ 皮卡丘生成失败")
        sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)

# 第二步：四图融合
print("🎨 第二步：四图融合...")
print()

# 四只宝可梦的正确 UUID
image_uuids = [
    pikachu_uuid,                                 # 皮卡丘（刚生成）
    "p_26d2197b-9da8-4cd6-a965-d7eb8e63f846",    # 杰尼龟
    "p_929c4dd4-a08b-4d04-b4c5-6f376ced439e",    # 妙蛙种子
    "p_54fca3b0-b203-4ad7-a014-1db7ac36fd51"     # 小火龙
]

print("融合素材（全部正确 UUID 格式）：")
print(f"  ⚡ 皮卡丘: {image_uuids[0]}")
print(f"  💧 杰尼龟: {image_uuids[1]}")
print(f"  🌿 妙蛙种子: {image_uuids[2]}")
print(f"  🔥 小火龙: {image_uuids[3]}")
print()

prompt = "A legendary fusion Pokemon combining Pikachu, Squirtle, Bulbasaur, and Charmander. Features: yellow electric cheeks, blue turtle shell on back, green plant bulb with vines, orange flame at tail tip. Cute yet powerful, digital art, high quality, white background, mythical creature"

print(f"📝 融合提示词: {prompt[:60]}...")
print(f"⚙️  使用模型: Kling O1")
print(f"⏳ 正在融合...")
print()

try:
    result = client.image_to_image(
        prompt=prompt,
        image_uuids=image_uuids,
        port="kling-image",
        strength=0.75,
        relevance=[0.85, 0.85, 0.85, 0.85],
        wh_ratio="1:1"
    )
    
    if result and len(result) > 0 and result[0].get('image'):
        fusion_uuid = result[0].get('image')
        print("="*60)
        print("✅ 融合成功！")
        print(f"📷 融合生物 UUID: {fusion_uuid}")
        print("="*60)
        print()
        print("🎉 诞生了一只融合四大初代宝可梦的神话生物！")
        print()
        print("生物特征：")
        print("  ⚡ 皮卡丘的黄色电击脸颊")
        print("  💧 杰尼龟的蓝色龟壳")  
        print("  🌿 妙蛙种子的绿色种子背")
        print("  🔥 小火龙的橙色火焰尾")
    else:
        print("❌ 融合失败")
        print(f"结果: {result}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
