#!/usr/bin/env python3
"""
第一步：生成三只宝可梦图片（杰尼龟、妙蛙种子、小火龙）
使用 Kling O1（快速）
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
print("第一步：生成三只宝可梦图片")
print("="*60)

client = create_client()

# 生成三只宝可梦
pokemons = [
    ("杰尼龟", "Squirtle, the tiny turtle Pokemon, blue shell, big eyes, cute, white background, digital art, high quality"),
    ("妙蛙种子", "Bulbasaur, the seed Pokemon, green body with bulb on back, red eyes, cute, white background, digital art, high quality"),
    ("小火龙", "Charmander, the lizard Pokemon, orange body, flame tail, blue eyes, cute, white background, digital art, high quality")
]

results = {}

for name, prompt in pokemons:
    print(f"\n🎨 生成 {name}...")
    print(f"   提示词: {prompt[:50]}...")
    
    try:
        result = client.text_to_image(
            prompt=prompt,
            port="kling-image",
            wh_ratio="1:1",
            batch_size=1
        )
        
        if result and len(result) > 0:
            image_uuid = result[0].get('image', 'N/A')
            print(f"   ✅ {name} 生成成功!")
            print(f"   📷 图片UUID: {image_uuid}")
            results[name] = image_uuid
        else:
            print(f"   ❌ {name} 生成失败")
    except Exception as e:
        print(f"   ❌ {name} 错误: {e}")

print("\n" + "="*60)
print("生成结果汇总：")
for name, uuid in results.items():
    print(f"  {name}: {uuid}")
print("="*60)
