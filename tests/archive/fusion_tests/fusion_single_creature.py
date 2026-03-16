#!/usr/bin/env python3
"""
重新融合 - 修复双头问题
强调单一生物、一个头、融合特征
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
print("🎨 重新融合 - 单一生物版")
print("="*60)
print()

client = create_client()

# 使用已有的四只宝可梦图片
image_uuids = [
    "p_100d4b4f-7b6e-417e-96bb-02794cb8bae9",    # 皮卡丘
    "p_26d2197b-9da8-4cd6-a965-d7eb8e63f846",    # 杰尼龟
    "p_929c4dd4-a08b-4d04-b4c5-6f376ced439e",    # 妙蛙种子
    "p_54fca3b0-b203-4ad7-a014-1db7ac36fd51"     # 小火龙
]

print("素材（相同的四只宝可梦）：")
print(f"  ⚡ 皮卡丘: {image_uuids[0][:20]}...")
print(f"  💧 杰尼龟: {image_uuids[1][:20]}...")
print(f"  🌿 妙蛙种子: {image_uuids[2][:20]}...")
print(f"  🔥 小火龙: {image_uuids[3][:20]}...")
print()

# 优化后的提示词 - 强调单一生物、一个头
prompt = "A single cute fusion Pokemon with ONE head and ONE body. Features: round yellow face with red electric cheeks like Pikachu, wearing a blue turtle shell like Squirtle on its back, green plant bulb with vines like Bulbasaur growing from shell, orange fire-tipped tail like Charmander. Standing pose, adorable expression, white background, high quality digital art, chibi style"

print("📝 优化后的提示词：")
print("   关键指令：")
print("   - 'single cute fusion Pokemon'（单一融合生物）")
print("   - 'ONE head and ONE body'（一个头、一个身体）")
print("   - 特征描述改为'戴着龟壳'、'尾巴有火焰'而不是拼在一起")
print()
print(f"   完整提示: {prompt[:80]}...")
print()
print(f"⚙️  参数：")
print(f"   模型: Kling O1")
print(f"   变化强度: 0.8（稍高，让融合更明显）")
print(f"   参考权重: [0.85, 0.85, 0.85, 0.85]")
print()
print("⏳ 正在生成单一生物融合...")
print()

try:
    result = client.image_to_image(
        prompt=prompt,
        image_uuids=image_uuids,
        port="kling-image",
        strength=0.8,
        relevance=[0.85, 0.85, 0.85, 0.85],
        wh_ratio="1:1"
    )
    
    if result and len(result) > 0 and result[0].get('image'):
        fusion_uuid = result[0].get('image')
        print("="*60)
        print("✅ 单一生物融合成功！")
        print(f"📷 新 UUID: {fusion_uuid}")
        print("="*60)
        print()
        print("🎉 应该只有一个头、一个身体的融合生物！")
        print()
        print("预期特征：")
        print("  ✓ 一个头（不是两个）")
        print("  ✓ 黄色圆脸 + 红色电击脸颊（皮卡丘）")
        print("  ✓ 背着蓝色龟壳（杰尼龟）")
        print("  ✓ 龟壳上长着绿色种子（妙蛙种子）")
        print("  ✓ 尾巴尖有火焰（小火龙）")
    else:
        print("❌ 融合失败")
        print(f"结果: {result}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
