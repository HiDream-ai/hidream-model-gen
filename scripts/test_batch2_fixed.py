#!/usr/bin/env python3
"""
第二批测试 - 修复版
"""

import sys
sys.path.insert(0, '.')

from vivago_client import create_client
from template_manager import get_template_manager
import requests
import time

client = create_client()
manager = get_template_manager()
image_uuid = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
headers_post = {**client.headers, 'Content-Type': 'application/json'}

# 第二批：20个 proto_transformer 模板
batch2 = [
    'renovation_of_old_photos', 'mystic_traveler', '1930s_vintage_style', 'autumn_feast',
    'magic_reveal_ravenclaw', 'animal_cooking', 'moving_figure', '1940s_suit_portrait',
    '2000s_y2k', '1960s_elegant', 'color_the_lines', '1970s_disco',
    '1990s_punk_rock', 'magic_reveal_gryffindor', 'doodle_alive', '1970s',
    'me_in_hand', 'music_box', 'a_family', 'turkey_chasing'
]

results = []

print('=' * 70)
print('第二批测试：proto_transformer 端口（20个模板）- 修复版')
print('=' * 70)

for i, template_id in enumerate(batch2, 1):
    try:
        template = manager.get_template(template_id)
        if not template:
            print(f'\\n[{i}/20] ❌ {template_id}: 模板不存在')
            results.append({'name': template_id, 'status': 'failed', 'error': 'template_not_found'})
            continue
        
        name = template.get('display_name', template_id)
        
        print(f'\\n[{i}/20] 测试: {name}')
        print('-' * 50)
        
        # 1. 提交任务
        print('  1. 提交...', end=' ', flush=True)
        data = manager.build_request_data(template_id, image_uuid, wh_ratio='9:16')
        url = f"{client.base_url}{template['endpoint']}"
        resp = requests.post(url, json=data, headers=headers_post, timeout=30)
        result = resp.json()
        
        if result.get('code') != 0:
            msg = result.get('message', '未知错误')
            print(f'❌ 失败: {msg}')
            results.append({'name': name, 'status': 'failed', 'error': 'submit_failed'})
            continue
        
        task_id = result.get('result', {}).get('task_id')
        print(f'✅ TaskID: {task_id[:8]}')
        
        # 2. 轮询结果
        print('  2. 轮询...', end=' ', flush=True)
        result_endpoint = template.get('result_endpoint')
        max_attempts = 30
        found_result = False
        
        for attempt in range(max_attempts):
            time.sleep(10)
            poll_url = f"{client.base_url}{result_endpoint}?task_id={task_id}"
            poll_resp = requests.get(poll_url, headers=client.headers, timeout=10)
            poll_data = poll_resp.json()
            
            if poll_data.get('code') == 0:
                sub_results = poll_data.get('result', {}).get('sub_task_results', [])
                if sub_results:
                    task_info = sub_results[0]
                    status = task_info.get('task_status', 0)
                    
                    if status == 1:
                        result_data = task_info.get('result', {})
                        if result_data.get('image'):
                            print(f'✅ 🖼️ 图片')
                            results.append({'name': name, 'status': 'passed', 'type': 'image'})
                        elif result_data.get('video'):
                            print(f'✅ 🎬 视频')
                            results.append({'name': name, 'status': 'passed', 'type': 'video'})
                        else:
                            print(f'✅ ? 未知')
                            results.append({'name': name, 'status': 'passed', 'type': 'unknown'})
                        found_result = True
                        break
                    elif status == 3:
                        print(f'❌ 失败')
                        results.append({'name': name, 'status': 'failed', 'error': 'task_failed'})
                        found_result = True
                        break
                    elif status == 4:
                        print(f'🚫 违规')
                        results.append({'name': name, 'status': 'rejected'})
                        found_result = True
                        break
        
        if not found_result:
            print(f'⏱️ 超时')
            results.append({'name': name, 'status': 'timeout'})
            
    except Exception as e:
        print(f'\\n[{i}/20] ⚠️ {template_id}: {str(e)[:40]}')
        results.append({'name': template_id, 'status': 'error', 'error': str(e)[:40]})
        continue

# 总结
print('\\n' + '=' * 70)
print('第二批测试完成')
print('=' * 70)

passed = [r for r in results if r['status'] == 'passed']
failed = [r for r in results if r['status'] == 'failed']
rejected = [r for r in results if r['status'] == 'rejected']
timeout = [r for r in results if r['status'] == 'timeout']
error = [r for r in results if r['status'] == 'error']

print(f'✅ 通过: {len(passed)}')
for r in passed:
    print(f'   - {r["name"]} ({r.get("type", "?")})')
if failed:
    print(f'\\n❌ 失败: {len(failed)}')
    for r in failed:
        print(f'   - {r["name"]}: {r.get("error", "")}')
if rejected:
    print(f'\\n🚫 违规: {len(rejected)}')
    for r in rejected:
        print(f'   - {r["name"]}')
if timeout:
    print(f'\\n⏱️ 超时: {len(timeout)}')
    for r in timeout:
        print(f'   - {r["name"]}')
if error:
    print(f'\\n⚠️ 错误: {len(error)}')
    for r in error:
        print(f'   - {r["name"]}: {r.get("error", "")}')

# 保存结果
import json
with open('/tmp/batch2_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'\\n✅ 结果已保存到 /tmp/batch2_results.json')
