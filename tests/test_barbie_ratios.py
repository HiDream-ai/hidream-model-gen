#!/usr/bin/env python3
"""
Barbie 模板比例测试
测试支持的比例: 9:16, 3:4, 1:1, 16:9
"""
import sys
import os

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from scripts.vivago_client import create_client
from tests.fixtures.cache_manager import get_cache_manager

# 测试比例
RATIOS = ['9:16', '3:4', '1:1', '16:9']

print('='*70)
print('Barbie 模板比例测试')
print('预估积分:', len(RATIOS) * 30)
print('='*70)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 tier3_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')
print('='*70)

results = []

for idx, ratio in enumerate(RATIOS, 1):
    print(f'\n[{idx}/{len(RATIOS)}] 🎭 Barbie 模板 - 比例 {ratio}')
    print(f'      积分: 30')
    print(f'      ⏳ 生成中...')
    
    try:
        result = client.template_to_video(
            image_uuid=test_uuid,
            template='barbie',
            wh_ratio=ratio
        )
        
        if result:
            print(f'      ✅ 成功! 比例 {ratio} 支持')
            results.append((ratio, '✅ 支持'))
        else:
            print(f'      ❌ 失败: 无结果')
            results.append((ratio, '❌ 失败'))
            
    except Exception as e:
        error_msg = str(e)
        if 'ratio' in error_msg.lower() or 'wh_ratio' in error_msg.lower():
            print(f'      ❌ 不支持: {error_msg[:50]}')
            results.append((ratio, f'❌ 不支持'))
        else:
            print(f'      ❌ 失败: {error_msg[:50]}')
            results.append((ratio, f'❌ 失败'))

# 打印汇总
print('\n' + '='*70)
print('Barbie 模板比例测试结果')
print('='*70)

for ratio, status in results:
    print(f'比例 {ratio:.<20} {status}')

supported = [r for r, s in results if '✅' in s]
unsupported = [r for r, s in results if '❌ 不支持' in s]
failed = [r for r, s in results if '❌ 失败' in s]

print('-'*70)
print(f'✅ 支持的比例: {supported}')
print(f'❌ 不支持的比例: {unsupported}')
print(f'⚠️  测试失败: {failed}')
print('='*70)

if unsupported:
    print('\n📌 结论: Barbie 模板确实只支持特定比例')
    print(f'   支持: {supported}')
    print(f'   不支持: {unsupported}')
else:
    print('\n📌 结论: Barbie 模板支持所有测试比例')
