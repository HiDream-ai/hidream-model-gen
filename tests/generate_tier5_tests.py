#!/usr/bin/env python3
"""
Tier 5: 模板采样测试 - 单个模板测试脚本生成器
为每个模板生成单独测试文件
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from template_manager import get_template_manager
from fixtures.cache_manager import get_cache_manager

# 采样模板列表 (40个代表模板)
SAMPLE_TEMPLATES = [
    # 风格类
    'ghibli', '1930s_vintage_style',
    # 哈利波特
    'magic_reveal_ravenclaw',
    # 翅膀
    'angel_wings', 'phoenix_wings',
    # 超级英雄
    'iron_man',
    # 舞蹈
    'apt',
    # 感恩节
    'turkey_chasing',
    # 特效
    'ash_out', 'metallic_liquid',
    # 漫画
    'gta_star',
    # 产品
    'glasses_display',
    # 场景
    'romantic_kiss',
    # 变身
    'barbie',
    # 照片修复
    'renovation_old_photos',
]

TEMPLATE_TEST_SCRIPT = '''#!/usr/bin/env python3
"""
Tier 5: 模板测试 - {template_id}
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
print('模板: {template_id}')
print('名称: {template_name}')
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

print(f'✅ 使用测试图片: {{test_uuid}}')
print('\\n⏳ 开始生成视频...')

try:
    result = client.template_to_video(
        image_uuid=test_uuid,
        template='{template_id}',
        wh_ratio='1:1'
    )
    
    print('\\n' + '='*60)
    print('✅ 模板 {template_id} 测试成功!')
    print('='*60)
    
    cache.save_test_result('template_{template_id}', {{'status': 'success'}})
    
except Exception as e:
    print('\\n' + '='*60)
    print('❌ 模板 {template_id} 测试失败')
    print('='*60)
    print(f'错误: {{e}}')
    cache.record_failure('templates', '{template_id}', str(e))
'''

def generate_template_tests():
    """为每个采样模板生成测试文件"""
    manager = get_template_manager()
    templates = manager.list_templates()
    
    test_dir = Path(__file__).parent / 'tier5_templates'
    test_dir.mkdir(exist_ok=True)
    
    generated = []
    
    for template_id in SAMPLE_TEMPLATES:
        if template_id not in templates:
            print(f'⚠️  模板 {template_id} 不存在，跳过')
            continue
        
        template_name = templates[template_id]
        
        # 生成测试文件
        script_content = TEMPLATE_TEST_SCRIPT.format(
            template_id=template_id,
            template_name=template_name
        )
        
        test_file = test_dir / f'test_template_{template_id}.py'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        generated.append(template_id)
        print(f'✅ 生成测试文件: {test_file}')
    
    # 生成运行脚本
    run_script = test_dir / 'run_all.sh'
    with open(run_script, 'w') as f:
        f.write('#!/bin/bash\n\n')
        f.write('# Tier 5: 批量运行模板测试\n\n')
        for tid in generated:
            f.write(f'echo "测试模板: {tid}"\n')
            f.write(f'python test_template_{tid}.py\n')
            f.write('sleep 5\n\n')
    
    print(f'\n📊 生成了 {len(generated)} 个模板测试文件')
    print(f'📁 位置: {test_dir}')
    print(f'🚀 运行单个测试: python {test_dir}/test_template_ghibli.py')

if __name__ == '__main__':
    generate_template_tests()
