#!/usr/bin/env python3
"""
使用 Nano Banana 融合四大初代宝可梦
皮卡丘 + 杰尼龟 + 妙蛙种子 + 小火龙
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
print("🎨 Nano Banana 宝可梦融合")
print("="*60)
print()
print("目标：创造一只融合四大初代宝可梦的生物")
print("  ⚡ 皮卡丘 (电)")
print("  💧 杰尼龟 (水)")
print("  🌿 妙蛙种子 (草)")
print("  🔥 小火龙 (火)")
print()

client = create_client()

# 检查是否有这些宝可梦的图片
# 从之前的测试记录中，我知道有 p_pikachu
# 但其他宝可梦需要先生成

print("📋 图片准备状态：")
print("  ✅ 皮卡丘: p_pikachu")
print("  ❌ 杰尼龟: 需要生成")
print("  ❌ 妙蛙种子: 需要生成")
print("  ❌ 小火龙: 需要生成")
print()
print("⚠️  需要先使用文生图生成其他三只宝可梦")
print("   然后用 Nano Banana 进行四图融合")
