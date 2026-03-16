#!/usr/bin/env python3
"""
Tier 5: 模板测试 - apt
积分: 30
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
print('Tier 5: 模板测试')
print('模板: apt')
print('名称: APT')
print('积分: 30')
print('='*60)
print('⚠️  提示: 视频生成需要2-5分钟')
print('='*60)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 test_tier3_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')
print('\n⏳ 开始生成视频...')

try:
    result = client.template_to_video(
        image_uuid=test_uuid,
        template='apt',
        wh_ratio='1:1'
    )
    
    print('\n' + '='*60)
    print('✅ 模板 apt 测试成功!')
    print('='*60)
    
    cache.save_test_result('template_apt', {'status': 'success'})
    
except Exception as e:
    print('\n' + '='*60)
    print('❌ 模板 apt 测试失败')
    print('='*60)
    print(f'错误: {e}')
    cache.record_failure('templates', 'apt', str(e))
