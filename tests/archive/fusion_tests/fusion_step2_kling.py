#!/usr/bin/env python3
"""
第二步（备用）：使用 Kling O1 融合四大初代宝可梦
Nano Banana 遇到服务器拥堵，改用 Kling O1
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
print("🎨 Kling O1 四图融合")
print("="*60)
print()
print("融合素材：")
print("  ⚡ 皮卡丘: p_pikachu")
print("  💧 杰尼龟: p_26d2197b-9da8-4cd6-a965-d7eb8e63f846")
print("  🌿 妙蛙种子: p_929c4dd4-a08b-4d04-b4c5-6f376ced439e")
print("  🔥 小火龙: p_54fca3b0-b203-4ad7-a014-1db7ac36fd51")
print()

client = create_client()

# 四只宝可梦的图片 UUID
image_uuids = [
    "p_pikachu",  # 皮卡丘
    "p_26d2197b-9da8-4cd6-a965-d7eb8e63f846",  # 杰尼龟
    "p_929c4dd4-a08b-4d04-b4c5-6f376ced439e",  # 妙蛙种子
    "p_54fca3b0-b203-4ad7-a014-1db7ac36fd51"   # 小火龙
]

prompt = "A fusion creature combining Pikachu, Squirtle, Bulbasaur, and Charmander. A mythical Pokemon with yellow electric cheeks, blue turtle shell on back, green bulb with vines, and orange flame tail. Cute, powerful, legendary, digital art, high quality, white background"

print(f"📝 融合提示词:")
print(f"   {prompt[:80]}...")
print()
print(f"⚙️  融合参数:")
print(f"   模型: Kling O1 (快速)")
print(f"   变化强度: 0.7")
print(f"   参考权重: [0.9, 0.9, 0.9, 0.9]")
print()
print("⏳ 正在融合...")
print()

try:
    result = client.image_to_image(
        prompt=prompt,
        image_uuids=image_uuids,
        port="kling-image",
        strength=0.7,
        relevance=[0.9, 0.9, 0.9, 0.9],
        wh_ratio="1:1"
    )
    
    if result and len(result) > 0 and result[0].get('image'):
        image_uuid = result[0].get('image')
        print("="*60)
        print("✅ 融合成功！")
        print(f"📷 融合生物图片UUID: {image_uuid}")
        print("="*60)
        print()
        print("🎉 诞生了一只融合四大初代宝可梦的神话生物！")
        print("   特征: 皮卡丘的电击脸颊 + 杰尼龟的龟壳 + 妙蛙种子的种子背 + 小火龙的火焰尾")
    else:
        print("❌ 融合失败")
        print(f"结果: {result}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
