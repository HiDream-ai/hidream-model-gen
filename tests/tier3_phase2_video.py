#!/usr/bin/env python3
"""
Tier 3 视频功能测试
允许长时间等待，不设置严格超时
"""
import sys
import os

# 添加正确的路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/tests')

from dotenv import load_dotenv
load_dotenv()

from scripts.vivago_client import create_client
from fixtures.cache_manager import get_cache_manager

print('='*60)
print('Tier 3 - Phase 2: 视频功能测试')
print('预估消耗: 90积分 (~¥3.8)')
print('预估时间: 10-20分钟 (取决于队列)')
print('='*60)
print('⚠️  提示: 视频生成可能需要较长时间，请耐心等待')
print('='*60)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 tier3_phase1_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')

results = {}

# Test 1: 图生视频 (v3L) - 20积分
print('\n[1/4] 🎬 图生视频 (v3L 360p) - 20积分...')
print('   ⏳ 预计等待 2-5 分钟 (含可能的队列等待)...')
try:
    result = client.image_to_video(
        prompt='camera slowly zooming out from the subject, gentle movement',
        image_uuid=test_uuid,
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    results['image_to_video'] = '✅ 成功'
    print(f'   ✅ 图生视频成功!')
except Exception as e:
    results['image_to_video'] = f'❌ 失败: {str(e)[:50]}'
    print(f'   ❌ 失败: {e}')

# Test 2: 文生视频 (v3L) - 20积分
print('\n[2/4] 📝 文生视频 (v3L 360p) - 20积分...')
print('   ⏳ 预计等待 2-5 分钟 (含可能的队列等待)...')
try:
    result = client.text_to_video(
        prompt='colorful balloons floating in the sky on a sunny day',
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    results['text_to_video'] = '✅ 成功'
    print(f'   ✅ 文生视频成功!')
except Exception as e:
    results['text_to_video'] = f'❌ 失败: {str(e)[:50]}'
    print(f'   ❌ 失败: {e}')

# Test 3: 视频首尾帧 (v3L) - 20积分
print('\n[3/4] 🎞️ 视频首尾帧 (v3L 360p) - 20积分...')
print('   ⏳ 预计等待 2-5 分钟 (含可能的队列等待)...')
try:
    result = client.keyframe_to_video(
        prompt='smooth transition effect',
        start_image_uuid=test_uuid,
        end_image_uuid=test_uuid,
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    results['keyframe_to_video'] = '✅ 成功'
    print(f'   ✅ 视频首尾帧成功!')
except Exception as e:
    results['keyframe_to_video'] = f'❌ 失败: {str(e)[:50]}'
    print(f'   ❌ 失败: {e}')

# Test 4: 视频模板 - 30积分
print('\n[4/4] 🎭 视频模板 - 30积分...')
print('   模板: ghibli (Ghibli style)')
print('   ⏳ 预计等待 2-5 分钟 (含可能的队列等待)...')
try:
    result = client.template_to_video(
        image_uuid=test_uuid,
        template='ghibli',
        wh_ratio='1:1'
    )
    results['template_to_video'] = '✅ 成功'
    print(f'   ✅ 视频模板成功!')
except Exception as e:
    results['template_to_video'] = f'❌ 失败: {str(e)[:50]}'
    print(f'   ❌ 失败: {e}')

# 保存结果
cache.save_test_result('tier3_phase2_video', results)

print('\n' + '='*60)
print('Tier 3 Phase 2 完成')
print('='*60)

print('\n📊 测试结果:')
for test, result in results.items():
    print(f'   {test}: {result}')

success_count = sum(1 for r in results.values() if '✅' in r)
print(f'\n✅ 通过: {success_count}/{len(results)}')

if success_count == len(results):
    print('\n🎉 视频功能全部正常!')
else:
    print(f'\n⚠️  {len(results) - success_count} 项测试失败')
