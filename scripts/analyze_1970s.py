#!/usr/bin/env python3
"""
1970s 模板调用问题分析
检查请求格式、端点、字段等
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://vivago.ai/api/gw"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiIyODg4Njc1NS0xOTA2LTRiY2YtODgzNC04MDFlNDM4OTliYWIiLCJ1c2VybmFtZSI6ImRpc2NvcmRfcUR6SVJvYiIsInBob25lbnVtIjoiMTIzNDU2Nzg5MTAiLCJlbWFpbCI6InpoYW9mYW5xaXVAZ21haWwuY29tIiwicm9sZSI6ImFwaSZlLWNvbW1lcmNlciZnZW5lcmFsIiwiZXhwIjo0ODY0ODc2MzM5fQ.pstbKg6H9I6KFG5fTPgpzkkrV6hd5YYoe0PbHV2YIYk"
IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'X-accept-language': 'en',
    'Content-Type': 'application/json'
}

print("="*60)
print("1970s 模板调用问题分析")
print("="*60)
print()

from scripts.template_manager import get_template_manager
manager = get_template_manager()
template = manager.get_template('1970s')

print("【模板配置信息】")
print(f"  Name: {template.get('name')}")
print(f"  Endpoint: {template.get('endpoint')}")
print(f"  Result Endpoint: {template.get('result_endpoint')}")
print(f"  Module: {template.get('module')}")
print(f"  Version: {template.get('version')}")
print(f"  Template ID: {template.get('template_id')}")
print(f"  Algo Type: {template.get('algo_type')}")
print()

# 获取原始参数
print("【原始参数】")
params = template.get('params', {})
print(f"  Module: {params.get('module')}")
print(f"  Version: {params.get('version')}")
print(f"  Template ID: {params.get('template_id')}")
print(f"  Prompt (原始): {params.get('prompt')[:100]}...")
print()

# 检查是否有 restricted_ratio
print("【模板限制】")
print(f"  Restricted Ratio: {template.get('restricted_ratio', False)}")
print(f"  Supported Ratios: {template.get('supported_ratios')}")
print()

# 构建请求并详细检查
data = manager.build_request_data('1970s', IMAGE_UUID, wh_ratio='1:1')

print("【构建的请求数据 - 详细检查】")
print(f"  顶层字段: {list(data.keys())}")
print()

# 检查是否有问题字段
print("  字段检查:")
print(f"    - module: {data.get('module')} {'✅' if data.get('module') else '❌'}")
print(f"    - version: {data.get('version')} {'✅' if data.get('version') else '❌'}")
print(f"    - template_id: {data.get('template_id')} {'✅' if data.get('template_id') else '❌'}")
print(f"    - images: {data.get('images')} {'✅' if data.get('images') else '❌'}")
print(f"    - params.module: {data.get('params', {}).get('module')} {'✅' if data.get('params', {}).get('module') else '❌'}")
print(f"    - params.custom_params: {'✅' if data.get('params', {}).get('custom_params') else '❌'}")

# 检查 custom_params
cc = data.get('params', {}).get('custom_params', {})
print(f"    - custom_params.master_template_id: {'✅' if cc.get('master_template_id') else '❌'}")
print(f"    - custom_params.prompts: {len(cc.get('prompts', []))} prompts")
print(f"    - custom_params.wh_ratio: {cc.get('wh_ratio')}")

# 对比 1940s_suit_portrait（成功的模板）
print()
print("【对比测试 - 1940s_suit_portrait (成功的模板)】")
template_1940s = manager.get_template('1940s_suit_portrait')
data_1940s = manager.build_request_data('1940s_suit_portrait', IMAGE_UUID, wh_ratio='1:1')

print(f"  1940s Endpoint: {template_1940s.get('endpoint')}")
print(f"  1940s Module: {template_1940s.get('module')}")
print(f"  1940s Algo Type: {template_1940s.get('algo_type')}")

cc_1940s = data_1940s.get('params', {}).get('custom_params', {})
print(f"  1940s Prompts count: {len(cc_1940s.get('prompts', []))}")
if cc_1940s.get('prompts'):
    print(f"  1940s First prompt length: {len(cc_1940s['prompts'][0])}")

# 关键对比
print()
print("【关键差异对比】")
print(f"  1970s - Endpoint: {template.get('endpoint')}")
print(f"  1940s - Endpoint: {template_1940s.get('endpoint')}")
print()
print(f"  1970s - Algo Type: {template.get('algo_type')}")
print(f"  1940s - Algo Type: {template_1940s.get('algo_type')}")
print()
print(f"  1970s - Prompts: {len(cc.get('prompts', []))}")
print(f"  1940s - Prompts: {len(cc_1940s.get('prompts', []))}")

# 发送对比请求
print()
print("="*60)
print("【发送测试】对比两个模板")
print("="*60)

for name, test_data in [('1970s', data), ('1940s_suit_portrait', data_1940s)]:
    template_info = manager.get_template(name)
    url = f"{BASE_URL}{template_info.get('endpoint')}"
    
    print(f"\n测试: {name}")
    print(f"  URL: {url}")
    print(f"  开始: {datetime.now().isoformat()}")
    
    start = time.time()
    try:
        resp = requests.post(url, json=test_data, headers=headers, timeout=30)
        elapsed = time.time() - start
        print(f"  响应时间: {elapsed:.2f}秒")
        print(f"  HTTP: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"  API Code: {result.get('code')}")
            print(f"  API Message: {result.get('message')}")
            if result.get('code') == 0:
                print(f"  ✅ 成功!")
            else:
                print(f"  ❌ API 错误: {result.get('message')}")
        else:
            print(f"  ❌ HTTP 错误: {resp.text[:100]}")
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"  ❌ 超时 ({elapsed:.2f}秒)")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ 错误: {type(e).__name__}: {e}")

print("\n" + "="*60)
print("分析完成")
print("="*60)
