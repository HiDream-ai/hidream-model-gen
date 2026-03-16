#!/usr/bin/env python3
"""
Tier 4: 视频端口单独测试 - Kling video O1
高积分端口，低频测试
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
print('Tier 4: 视频端口测试 - Kling video O1')
print('功能: 文生视频 / 图生视频')
print('积分: 80/次 (高积分端口，建议低频测试)')
print('='*60)
print('⚠️  提示: 这是高积分端口，测试前请确认')
print('='*60)

confirm = input('确认测试 Kling video O1 (80积分)? [y/N]: ')
if confirm.lower() != 'y':
    print('已取消')
    sys.exit(0)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 test_tier3_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')

# 测试: 图生视频 - 80积分
print('\n🎬 Kling video O1 图生视频 - 80积分...')
print('   ⏳ 预计等待 2-5 分钟...')
print('   这是高质量视频生成，积分消耗较高')

try:
    result = client.image_to_video(
        prompt='cinematic shot with professional lighting',
        image_uuid=test_uuid,
        port='kling-video',
        duration=5,
        wh_ratio='1:1'
    )
    print('   ✅ Kling video O1 成功!')
    cache.save_test_result('port_kling_video', {'status': 'success'})
except Exception as e:
    print(f'   ❌ 失败: {e}')
    cache.record_failure('ports', 'kling_video', str(e))

print('\n' + '='*60)
print('Tier 4 Kling video 端口测试完成')
print('='*60)
