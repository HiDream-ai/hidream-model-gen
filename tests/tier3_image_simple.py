#!/usr/bin/env python3
"""
Tier 3: 核心功能冒烟测试 - 图片功能流水线 (简化版)
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

from scripts.vivago_client import create_client
import time

print('='*60)
print('Tier 3 - Phase 1: 图片功能测试')
print('预估消耗: 8积分 (~¥0.3)')
print('预估时间: 30-60秒')
print('='*60)

client = create_client()

# Test 1: 文生图 (Kling O1) - 8积分
print('\n[1/1] 🎨 文生图 (Kling O1) - 8积分...')
print('   ⏳ 提交任务...')

try:
    result = client.text_to_image(
        prompt='a cute cartoon cat playing with a ball of yarn, colorful and cheerful',
        port='kling-image',
        batch_size=1,
        wh_ratio='1:1'
    )
    
    print(f'   ✅ 文生图成功!')
    print(f'   生成图片数: {len(result)}')
    
    if result and len(result) > 0:
        image_info = result[0]
        print(f'   图片ID: {image_info.get("image", "N/A")}')
        print(f'   任务状态: {image_info.get("task_status", "N/A")}')
        
    print('\n' + '='*60)
    print('✅ Tier 3 图片功能测试通过!')
    print('='*60)
    
except Exception as e:
    print(f'   ❌ 文生图失败: {e}')
    import traceback
    traceback.print_exc()
    print('\n' + '='*60)
    print('❌ Tier 3 图片功能测试失败!')
    print('='*60)
    sys.exit(1)
