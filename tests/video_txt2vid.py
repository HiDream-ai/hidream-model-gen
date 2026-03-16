#!/usr/bin/env python3
"""
视频功能单独测试 - 文生视频
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from scripts.vivago_client import create_client
from tests.fixtures.cache_manager import get_cache_manager

print('='*60)
print('视频测试: 文生视频 (Text-to-Video)')
print('端口: v3L (360p)')
print('积分: 20')
print('='*60)

client = create_client()
cache = get_cache_manager()

print('⏳ 开始生成视频，请耐心等待...')
print('   提示: 视频生成可能需要 2-5 分钟')
print()

try:
    result = client.text_to_video(
        prompt='colorful balloons floating in the sky on a sunny day',
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    
    print('\n' + '='*60)
    print('✅ 文生视频成功!')
    print('='*60)
    print(f'\n📊 结果:')
    print(f'   生成视频数: {len(result) if result else 0}')
    if result:
        print(f'   视频信息: {result[0] if isinstance(result, list) else result}')
    
    cache.save_test_result('video_txt2vid', {'status': 'success', 'count': len(result) if result else 0})
    
except Exception as e:
    print('\n' + '='*60)
    print('❌ 文生视频失败')
    print('='*60)
    print(f'错误: {e}')
    cache.record_failure('video_tests', 'txt2vid', str(e))
