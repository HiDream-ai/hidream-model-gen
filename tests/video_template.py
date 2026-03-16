#!/usr/bin/env python3
"""
视频功能单独测试 - 视频模板
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from scripts.vivago_client import create_client
from tests.fixtures.cache_manager import get_cache_manager

print('='*60)
print('视频测试: 视频模板 (Template-to-Video)')
print('模板: ghibli')
print('积分: 30')
print('='*60)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 tier3_phase1_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')
print('\n⏳ 开始生成视频，请耐心等待...')
print('   提示: 视频生成可能需要 2-5 分钟')
print()

try:
    result = client.template_to_video(
        image_uuid=test_uuid,
        template='ghibli',
        wh_ratio='1:1'
    )
    
    print('\n' + '='*60)
    print('✅ 视频模板成功!')
    print('='*60)
    print(f'\n📊 结果:')
    print(f'   生成视频数: {len(result) if result else 0}')
    
    cache.save_test_result('video_template', {'status': 'success'})
    
except Exception as e:
    print('\n' + '='*60)
    print('❌ 视频模板失败')
    print('='*60)
    print(f'错误: {e}')
    cache.record_failure('video_tests', 'template', str(e))
