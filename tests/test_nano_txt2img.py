#!/usr/bin/env python3
"""
Nano Banana 文生图功能测试
积分: 10 (Nano Banana)
特点: 高质量但较慢
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
print("Nano Banana 文生图功能测试")
print("预估积分: 10")
print("特点: 高质量生成，较慢速度")
print("="*60)

client = create_client()

print("\n🎨 生成中...")
print("⏳ Nano Banana 通常需要 1-3 分钟...")

try:
    result = client.text_to_image(
        prompt='一只开心的哆啦A梦在草地上玩耍，阳光明媚，色彩鲜艳，高清细节',
        port='nano-banana',
        batch_size=1,
        wh_ratio='1:1'
    )
    
    if result and len(result) > 0:
        image_id = result[0].get('image', 'N/A')
        print(f"\n✅ 生成成功!")
        print(f"   图片ID: {image_id}")
        
        # 构建下载链接
        if image_id.startswith('p_'):
            clean_id = image_id[2:]
        else:
            clean_id = image_id
        url = f"https://storage.vivago.ai/image/{clean_id}.jpg"
        print(f"   下载链接: {url}")
        
        print("\n" + "="*60)
        print("✅ Nano Banana 文生图功能正常!")
        print("="*60)
    else:
        print("\n❌ 生成失败: 无结果返回")
        
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
