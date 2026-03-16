#!/usr/bin/env python3
"""
Tier 5: 剩余6个模板测试 (排除已失效的 barbie)
积分: 180 (30 x 6)
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

# 剩余6个测试模板 (barbie 已标记为失效)
TEMPLATES = [
    ('apt', 'APT舞蹈'),
    ('ash_out', '灰烬特效'),
    ('gta_star', 'GTA风格'),
    ('phoenix_wings', '凤凰翅膀'),
    ('turkey_chasing', '火鸡追逐'),
    ('magic_reveal_ravenclaw', '哈利波特-拉文克劳'),  # 重新验证
]

print('='*70)
print('Tier 5: 剩余6个模板测试')
print(f'预估积分: {len(TEMPLATES) * 30} ({len(TEMPLATES)} x 30)')
print('='*70)
print('⚠️  注意: barbie 模板已标记为失效，跳过测试')
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

for idx, (template_id, template_name) in enumerate(TEMPLATES, 1):
    print(f'\n[{idx}/{len(TEMPLATES)}] 🎭 {template_name} ({template_id})')
    print(f'      积分: 30')
    print(f'      ⏳ 生成中...')
    
    try:
        result = client.template_to_video(
            image_uuid=test_uuid,
            template=template_id,
            wh_ratio='1:1'
        )
        
        if result:
            print(f'      ✅ 成功!')
            results.append((template_id, template_name, '✅ 成功'))
            cache.save_test_result(f'template_{template_id}', {'status': 'success', 'name': template_name})
        else:
            print(f'      ❌ 失败: 无结果')
            results.append((template_id, template_name, '❌ 失败'))
            
    except Exception as e:
        print(f'      ❌ 失败: {e}')
        results.append((template_id, template_name, f'❌ 失败: {str(e)[:30]}'))

# 打印汇总
print('\n' + '='*70)
print('Tier 5 剩余模板测试完成')
print('='*70)

for template_id, name, status in results:
    print(f'{name:.<40} {status}')

passed = sum(1 for _, _, s in results if '✅' in s)
total_credits = passed * 30

print('-'*70)
print(f'结果: {passed}/{len(TEMPLATES)} 通过')
print(f'积分消耗: {total_credits}/{len(TEMPLATES) * 30}')
print('='*70)

# 添加历史记录
print('\n📊 Tier 5 累计测试结果:')
print('  ✅ ghibli (吉卜力)')
print('  ✅ iron_man (钢铁侠)')
print('  ✅ angel_wings (天使翅膀)')
print('  ❌ barbie (芭比) - 已标记失效')

for template_id, name, status in results:
    print(f'  {status[:1]} {template_id} ({name})')

if passed == len(TEMPLATES):
    print('\n🎉 所有剩余模板测试通过!')
else:
    print(f'\n⚠️  {len(TEMPLATES) - passed} 个模板失败')
