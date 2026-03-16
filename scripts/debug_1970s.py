#!/usr/bin/env python3
"""
1970s 模板深度调试
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

import requests
import json
import time
from datetime import datetime

# 直接构造最小化测试
BASE_URL = "https://vivago.ai/api/gw"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiIyODg4Njc1NS0xOTA2LTRiY2YtODgzNC04MDFlNDM4OTliYWIiLCJ1c2VybmFtZSI6ImRpc2NvcmRfcUR6SVJvYiIsInBob25lbnVtIjoiMTIzNDU2Nzg5MTAiLCJlbWFpbCI6InpoYW9mYW5xaXVAZ21haWwuY29tIiwicm9sZSI6ImFwaSZlLWNvbW1lcmNlciZnZW5lcmFsIiwiZXhwIjo0ODY0ODc2MzM5fQ.pstbKg6H9I6KFG5fTPgpzkkrV6hd5YYoe0PbHV2YIYk"
IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'X-accept-language': 'en',
    'Content-Type': 'application/json'
}

print("="*60)
print("1970s 模板深度调试")
print("="*60)
print(f"时间: {datetime.now().isoformat()}")
print()

# 测试 1: 使用 template_manager 构建的请求
print("【测试 1】使用 template_manager 构建请求")
print("-"*60)

from scripts.template_manager import get_template_manager
manager = get_template_manager()
template = manager.get_template('1970s')

print(f"模板信息:")
print(f"  Name: {template.get('name')}")
print(f"  Endpoint: {template.get('endpoint')}")
print(f"  Module: {template.get('module')}")
print(f"  Template ID: {template.get('template_id')}")

data1 = manager.build_request_data('1970s', IMAGE_UUID, wh_ratio='1:1')
print(f"\n请求数据 (template_manager 构建):")
print(f"  Module: {data1.get('module')}")
print(f"  Template ID: {data1.get('template_id')}")
print(f"  Images: {data1.get('images')}")
print(f"  Params keys: {list(data1.get('params', {}).keys())}")

custom_params = data1.get('params', {}).get('custom_params', {})
print(f"  Custom params keys: {list(custom_params.keys())}")
print(f"  Prompts count: {len(custom_params.get('prompts', []))}")
if custom_params.get('prompts'):
    print(f"  First prompt length: {len(custom_params['prompts'][0])}")

# 测试 2: 手动构建最小请求
print("\n" + "="*60)
print("【测试 2】手动构建最小请求")
print("-"*60)

data2 = {
    "module": "proto_transformer",
    "version": "v1",
    "prompt": "",
    "images": [IMAGE_UUID],
    "masks": [],
    "videos": [],
    "audios": [],
    "params": {
        "mode": "Fast",
        "style": "default",
        "height": -1,
        "width": -1,
        "seed": -1,
        "duration": 5,
        "motion": 0,
        "x": 0,
        "y": 0,
        "z": 0,
        "reserved_str": "",
        "batch_size": 1,
        "wh_ratio": "1:1",
        "custom_params": {
            "prompts": ["A glamorous 1970s disco style portrait"],
            "master_template_id": "4f12d18f-ca18-45ec-8b22-495184deed61.mp4",
            "wh_ratio": "1:1"
        }
    },
    "template_id": "4f12d18f-ca18-45ec-8b22-495184deed61.mp4"
}

print(f"手动构建请求:")
print(f"  Module: {data2.get('module')}")
print(f"  Template ID: {data2.get('template_id')}")
print(f"  Prompt (简化): A glamorous 1970s disco style portrait")

# 比较两个请求
print("\n" + "="*60)
print("【比较】两个请求的差异")
print("-"*60)

print(f"\nTemplate Manager 构建的 prompts[0]:")
if custom_params.get('prompts'):
    p1 = custom_params['prompts'][0]
    print(f"  长度: {len(p1)}")
    print(f"  内容前100字符: {p1[:100]}...")

print(f"\n手动构建的 prompts[0]:")
p2 = "A glamorous 1970s disco style portrait"
print(f"  长度: {len(p2)}")
print(f"  内容: {p2}")

# 测试 3: 发送简化请求
print("\n" + "="*60)
print("【测试 3】发送简化请求 (短 prompt)")
print("-"*60)

url = f"{BASE_URL}/v3/pipeline/proto_transformer/async"
print(f"URL: {url}")
print(f"开始发送... {datetime.now().isoformat()}")

start = time.time()
try:
    resp = requests.post(url, json=data2, headers=headers, timeout=60)
    elapsed = time.time() - start
    print(f"响应时间: {elapsed:.2f}秒")
    print(f"HTTP 状态: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"API Code: {result.get('code')}")
        print(f"API Message: {result.get('message')}")
        
        if result.get('code') == 0:
            task_id = result.get('result', {}).get('task_id')
            print(f"✅ 成功! TaskID: {task_id}")
        else:
            print(f"❌ API 错误: {result.get('message')}")
    else:
        print(f"❌ HTTP 错误: {resp.text[:200]}")
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"❌ 超时 ({elapsed:.2f}秒)")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ 错误 ({elapsed:.2f}秒): {type(e).__name__}: {e}")

print("\n" + "="*60)
print("调试完成")
print("="*60)
