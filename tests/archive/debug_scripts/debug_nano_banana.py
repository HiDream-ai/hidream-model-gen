#!/usr/bin/env python3
"""
调试 Nano Banana 文生图功能
添加详细日志分析失败原因
"""
import sys
import os
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))

from dotenv import load_dotenv
load_dotenv()

from vivago_client import create_client
from fixtures.cache_manager import get_cache_manager

print('='*70)
print('🔍 调试 Nano Banana 文生图功能')
print('='*70)

client = None
try:
    print('\n[1/5] 初始化客户端...')
    client = create_client()
    print('   ✅ 客户端初始化成功')
    print(f'   Token: {client.token[:20]}...')
    
    print('\n[2/5] 获取端口配置...')
    config, port_name = client._get_port_config('text_to_image', 'nano-banana')
    print(f'   ✅ 端口配置获取成功: {port_name}')
    print(f'   Endpoint: {config.get("endpoint", "N/A")}')
    print(f'   Version: {config.get("version", "N/A")}')
    
    print('\n[3/5] 构建请求参数...')
    payload = {
        "module": "image_gen_std",
        "version": "nano-banana",
        "prompt": "fresh fruit arrangement",
        "en_prompt": "",
        "negative_prompt": "",
        "en_negative_prompt": "",
        "magic_prompt": "",
        "style": "default",
        "width": -1,
        "height": -1,
        "images": [],
        "masks": [],
        "params": {
            "wh_ratio": "1:1",
            "batch_size": 1,
            "mode": "2K",
            "seed": -1
        }
    }
    print('   ✅ 参数构建完成')
    print(f'   Prompt: {payload["prompt"]}')
    
    print('\n[4/5] 发送API请求...')
    print(f"   POST {config['endpoint']}")
    print('   ⏳ 等待响应 (可能需要10-30秒)...')
    
    import requests
    url = f"{client.base_url}{config['endpoint']}"
    response = requests.post(
        url,
        headers=client.headers,
        json=payload,
        timeout=60
    )
    
    print(f'   ✅ 收到响应: HTTP {response.status_code}')
    
    result = response.json()
    print(f'   响应内容: {result}')
    
    if result.get('code') != 0:
        print(f"   ❌ API返回错误: code={result.get('code')}, msg={result.get('msg')}")
        raise Exception(f"API error: {result.get('msg')}")
    
    task_id = result['result']['task_id']
    print(f'   ✅ 任务创建成功: {task_id}')
    
    print('\n[5/5] 轮询任务结果...')
    print(f"   GET {config['result_endpoint']}")
    print('   ⏳ 等待图片生成 (可能需要1-2分钟)...')
    
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        time.sleep(3)
        
        poll_payload = {"task_id": task_id}
        poll_response = requests.post(
            f"{client.base_url}{config['result_endpoint']}",
            headers=client.headers,
            json=poll_payload,
            timeout=30
        )
        
        poll_result = poll_response.json()
        
        if poll_result.get('code') == 0:
            result_data = poll_result.get('result', {})
            sub_results = result_data.get('sub_task_results', [])
            
            if sub_results:
                task_info = sub_results[0]
                status = task_info.get('task_status', 0)
                
                if status == 1:
                    print(f'   ✅ 任务完成! (尝试 {attempt}/{max_attempts})')
                    print(f'   生成图片数: {len(task_info.get("result", []))}')
                    
                    # 保存成功记录
                    cache = get_cache_manager()
                    cache.save_test_result('nano_banana_debug', {
                        'status': 'success',
                        'attempts': attempt,
                        'task_id': task_id
                    })
                    
                    print('\n' + '='*70)
                    print('✅ Nano Banana 调试成功')
                    print('='*70)
                    break
                
                elif status == 3:
                    print(f'   ❌ 任务失败 (尝试 {attempt}/{max_attempts})')
                    raise Exception("Task failed")
                
                elif status == 4:
                    print(f'   ❌ 内容被拒绝 (尝试 {attempt}/{max_attempts})')
                    raise Exception("Content rejected")
                
                else:
                    if attempt % 5 == 0:
                        print(f'   ⏳ 处理中... (尝试 {attempt}/{max_attempts})')
        else:
            if attempt % 5 == 0:
                print(f'   ⏳ 轮询中... code={poll_result.get("code")}')
    
    else:
        print(f'   ❌ 超时: 超过最大尝试次数 {max_attempts}')
        raise TimeoutError("Polling timeout")

except Exception as e:
    print('\n' + '='*70)
    print('❌ Nano Banana 调试失败')
    print('='*70)
    print(f'错误类型: {type(e).__name__}')
    print(f'错误信息: {e}')
    print('\n详细堆栈:')
    traceback.print_exc()
    
    # 保存失败记录
    try:
        cache = get_cache_manager()
        cache.save_test_result('nano_banana_debug', {
            'status': 'failed',
            'error': str(e),
            'error_type': type(e).__name__
        })
    except:
        pass
    
    sys.exit(1)
