#!/usr/bin/env python3
"""
第二批测试 - 重试失败的模板
"""

import sys
sys.path.insert(0, '.')

from vivago_client import create_client
from template_manager import get_template_manager
import requests
import json
import time

client = create_client()
manager = get_template_manager()
image_uuid = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
headers_post = {**client.headers, 'Content-Type': 'application/json'}

# 需要重试的13个模板
retry_templates = [
    'renovation_of_old_photos', '1930s_vintage_style', 'magic_reveal_ravenclaw',
    'animal_cooking', '1940s_suit_portrait', '2000s_y2k', 'color_the_lines',
    '1970s_disco', '1990s_punk_rock', 'magic_reveal_gryffindor', 'me_in_hand',
    'music_box', 'turkey_chasing'
]

results = []

print('=' * 70)
print('第二批测试 - 重试失败的模板（13个）')
print('=' * 70)

for i, template_id in enumerate(retry_templates, 1):
    try:
        template = manager.get_template(template_id)
        if not template:
            print(f'\\n[{i}/13] ❌ {template_id}: 模板不存在')
            results.append({'name': template_id, 'status': 'failed', 'error': 'template_not_found'})
            continue
        
        name = template.get('display_name', template_id)
        
        print(f'\\n[{i}/13] 测试: {name}')
        print('-' * 50)
        
        # 1. 提交任务（增加重试）
        print('  1. 提交...', end=' ', flush=True)
        
        submit_success = False
        for retry in range(3):  # 提交重试3次
            try:
                data = manager.build_request_data(template_id, image_uuid, wh_ratio='9:16')
                url = f"{client.base_url}{template['endpoint']}"
                resp = requests.post(url, json=data, headers=headers_post, timeout=60)
                result = resp.json()
                
                if result.get('code') != 0:
                    msg = result.get('message', '未知错误')
                    print(f'❌ 失败: {msg}')
                    results.append({'name': name, 'status': 'failed', 'error': 'submit_failed'})
                    break
                
                task_id = result.get('result', {}).get('task_id')
                print(f'✅ TaskID: {task_id[:8]}')
                submit_success = True
                break
                
            except Exception as e:
                if retry < 2:
                    print(f'⚠️ 重试{retry+1}...', end=' ', flush=True)
                    time.sleep(5)
                else:
                    print(f'❌ 提交失败: {str(e)[:40]}')
                    results.append({'name': name, 'status': 'error', 'error': str(e)[:40]})
        
        if not submit_success:
            continue
        
        # 2. 轮询结果
        print('  2. 轮询...', end=' ', flush=True)
        result_endpoint = template.get('result_endpoint')
        max_attempts = 30
        found_result = False
        
        for attempt in range(max_attempts):
            time.sleep(10)
            try:
                poll_url = f"{client.base_url}{result_endpoint}?task_id={task_id}"
                poll_resp = requests.get(poll_url, headers=client.headers, timeout=30)
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
            except Exception as e:
                pass  # 继续轮询
        
        if not found_result:
            print(f'⏱️ 超时')
            results.append({'name': name, 'status': 'timeout'})
            
    except Exception as e:
        print(f'\\n[{i}/13] ⚠️ {template_id}: {str(e)[:40]}')
        results.append({'name': template_id, 'status': 'error', 'error': str(e)[:40]})
        continue

# 总结
print('\\n' + '=' * 70)
print('第二批重试测试完成')
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
with open('/tmp/batch2_retry_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'\\n✅ 结果已保存到 /tmp/batch2_retry_results.json')
