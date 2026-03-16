#!/usr/bin/env python3
"""
Tier 4: 视频端口单独测试 - v3L
必须单独运行，避免超时
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
print('Tier 4: 视频端口测试 - v3L (Vivago 360p)')
print('功能: 图生视频 / 文生视频 / 视频首尾帧')
print('积分: 20-60 (根据测试项)')
print('='*60)
print('⚠️  提示: 视频生成需要2-5分钟，请耐心等待')
print('='*60)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 test_tier3_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')

# 测试1: 图生视频 - 20积分
print('\n[1/3] 🎬 图生视频 (v3L) - 20积分...')
print('   ⏳ 预计等待 2-5 分钟...')

try:
    result = client.image_to_video(
        prompt='gentle camera movement showing the subject',
        image_uuid=test_uuid,
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    print('   ✅ 图生视频成功!')
    cache.save_test_result('port_v3l_img2vid', {'status': 'success'})
except Exception as e:
    print(f'   ❌ 失败: {e}')
    cache.record_failure('ports', 'v3L_img2vid', str(e))

# 测试2: 文生视频 - 20积分
print('\n[2/3] 📝 文生视频 (v3L) - 20积分...')
print('   ⏳ 预计等待 2-5 分钟...')

try:
    result = client.text_to_video(
        prompt='peaceful nature scene with flowing water',
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    print('   ✅ 文生视频成功!')
    cache.save_test_result('port_v3l_txt2vid', {'status': 'success'})
except Exception as e:
    print(f'   ❌ 失败: {e}')
    cache.record_failure('ports', 'v3L_txt2vid', str(e))

# 测试3: 视频首尾帧 - 20积分
print('\n[3/3] 🎞️ 视频首尾帧 (v3L) - 20积分...')
print('   ⏳ 预计等待 2-5 分钟...')

try:
    result = client.keyframe_to_video(
        prompt='smooth morphing transition',
        start_image_uuid=test_uuid,
        end_image_uuid=test_uuid,
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    print('   ✅ 视频首尾帧成功!')
    cache.save_test_result('port_v3l_keyframe', {'status': 'success'})
except Exception as e:
    print(f'   ❌ 失败: {e}')
    cache.record_failure('ports', 'v3L_keyframe', str(e))

print('\n' + '='*60)
print('Tier 4 v3L 端口测试完成')
print('='*60)
