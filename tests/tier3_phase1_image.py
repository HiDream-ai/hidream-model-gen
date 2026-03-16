#!/usr/bin/env python3
"""
Tier 3 图片功能测试
低成本，快速验证
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))

from dotenv import load_dotenv
load_dotenv()

from vivago_client import create_client
from fixtures.cache_manager import get_cache_manager

print('='*60)
print('Tier 3 - Phase 1: 图片功能测试')
print('预估消耗: 16积分 (~¥0.7)')
print('预估时间: 30-60秒')
print('='*60)

client = create_client()
cache = get_cache_manager()

results = {}

# Test 1: 文生图 (Kling O1) - 8积分
print('\n[1/2] 🎨 文生图 (Kling O1) - 8积分...')
try:
    result = client.text_to_image(
        prompt='a cute cartoon cat playing with a ball of yarn, colorful and cheerful',  # 避免敏感内容
        port='kling-image',
        batch_size=1,
        wh_ratio='1:1'
    )
    results['text_to_image'] = '✅ 成功'
    print(f'   ✅ 成功，生成 {len(result)} 张图片')
    image_id = result[0].get('image', 'N/A') if result else 'N/A'
    print(f'   📷 图片ID: {image_id}')
except Exception as e:
    results['text_to_image'] = f'❌ 失败: {str(e)[:50]}'
    print(f'   ❌ 失败: {e}')

# Test 2: 图生图 - 需要上传图片先
print('\n[2/2] 🔄 图生图 (Kling O1) - 8积分...')

test_uuid = cache.get_image_uuid('portrait')
if not test_uuid:
    print('   📤 上传测试图片...')
    test_uuid = client.upload_image('tests/fixtures/images/portrait.jpg')
    cache.save_image_uuid('portrait', test_uuid)
    print(f'   ✅ 图片已上传: {test_uuid}')
else:
    print(f'   ✅ 使用缓存图片: {test_uuid}')

try:
    result = client.image_to_image(
        prompt='convert to watercolor painting style, artistic and beautiful',
        image_uuids=[test_uuid],
        port='kling-image',
        strength=0.7
    )
    results['image_to_image'] = '✅ 成功'
    print(f'   ✅ 成功')
except Exception as e:
    results['image_to_image'] = f'❌ 失败: {str(e)[:50]}'
    print(f'   ❌ 失败: {e}')

# 保存结果
cache.save_test_result('tier3_phase1_image', results)

print('\n' + '='*60)
print('Tier 3 Phase 1 完成')
print('='*60)

print('\n📊 测试结果:')
for test, result in results.items():
    print(f'   {test}: {result}')

success_count = sum(1 for r in results.values() if '✅' in r)
print(f'\n✅ 通过: {success_count}/{len(results)}')

if success_count == len(results):
    print('\n🎉 图片功能全部正常!')
    print('   可以运行 phase2_video.py 测试视频功能')
else:
    print('\n⚠️  部分测试失败，请检查')
