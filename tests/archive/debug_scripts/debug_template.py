#!/usr/bin/env python3
"""
视频模板单独调试
测试 ghibli 模板
"""
import sys
import os
import json
import requests

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

TOKEN = os.environ.get('HIDREAM_TOKEN')
BASE_URL = "https://vivago.ai/api/gw"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-accept-language": "en",
    "Content-Type": "application/json"
}

print("="*60)
print("视频模板单独调试 - ghibli")
print("="*60)

# 获取模板配置
print("\n📋 Step 1: 获取 ghibli 模板配置")
from template_manager import get_template_manager
tm = get_template_manager()
template = tm.get_template("ghibli")
print(f"模板配置: {json.dumps(template, indent=2, ensure_ascii=False)[:500]}")

# 准备请求数据
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"

# 构建请求体 (参考 api_ports.json 中的配置)
request_data = {
    "module": "style_transformer",
    "version": "v1",
    "prompt": "",
    "images": [image_uuid],
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
        "wh_ratio": "9:16",
        "custom_params": {
            "wh_ratio": "9:16",
            "template_id": "51c6856c-60ec-4a32-8855-0a8251ededfb.mp4"
        }
    },
    "request_id": "debug-ghibli-001"
}

# 尝试不同的端点
endpoints_to_try = [
    "/v3/pipeline/style_transformer/async",
    "/v3/video/video_diffusion_template/async",
    "/v3/video/video_diffusion_img2vid/async"
]

print("\n📤 Step 2: 尝试提交任务")
for endpoint in endpoints_to_try:
    url = f"{BASE_URL}{endpoint}"
    print(f"\n尝试端点: {endpoint}")
    
    try:
        resp = requests.post(url, headers=headers, json=request_data, timeout=30)
        result = resp.json()
        print(f"状态码: {resp.status_code}")
        print(f"响应: {json.dumps(result, indent=2)}")
        
        if result.get('code') == 0:
            print(f"✅ 成功! 任务已提交")
            task_id = result.get('result', {}).get('task_id')
            if task_id:
                print(f"任务ID: {task_id}")
            break
        else:
            print(f"❌ 失败: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

print("\n" + "="*60)
print("调试完成")
print("="*60)
