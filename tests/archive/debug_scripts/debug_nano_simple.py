#!/usr/bin/env python3
"""
调试 Nano Banana - 使用已知正确的参数
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from dotenv import load_dotenv
load_dotenv()

import requests

print('='*70)
print('🔍 调试 Nano Banana - 简化版本')
print('='*70)

# 直接构造请求
token = os.getenv('HIDREAM_TOKEN')
headers = {
    "Authorization": f"Bearer {token}",
    "X-accept-language": "en",
}

# 测试不同的 module 和参数组合
test_configs = [
    {
        "name": "标准配置",
        "module": "image_gen_std",
        "version": "nano-banana-2",
        "mode": "2K"
    },
    {
        "name": "备选配置1",
        "module": "image_gen_std",
        "version": "nano-banana",
        "mode": "Fast"
    },
    {
        "name": "备选配置2",
        "module": "nano-banana",
        "version": "v1",
        "mode": "Fast"
    }
]

for i, cfg in enumerate(test_configs, 1):
    print(f"\n[测试 {i}] {cfg['name']}")
    print(f"  module: {cfg['module']}")
    print(f"  version: {cfg['version']}")
    print(f"  mode: {cfg['mode']}")
    
    payload = {
        "module": cfg['module'],
        "version": cfg['version'],
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
            "mode": cfg['mode'],
            "seed": -1
        }
    }
    
    try:
        response = requests.post(
            'https://vivago.ai/api/gw/v3/image/image_gen_std/async',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        result = response.json()
        print(f"  结果: code={result.get('code')}, msg={result.get('msg', result.get('message', 'N/A'))}")
        
        if result.get('code') == 0:
            print(f"  ✅ 成功! task_id={result['result']['task_id']}")
            break
        else:
            print(f"  ❌ 失败")
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")

print('\n' + '='*70)
