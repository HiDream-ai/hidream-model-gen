#!/usr/bin/env python3
"""
新图片上传方式测试
验证 Vivago AI 新的图片上传接口

新流程:
1. GET /prod-api/user/google_key/hidreamai-image?filename=xxx&content_type=image/jpeg
   → 返回预签名 URL
2. PUT 预签名 URL (data=图片二进制) → 完成上传
"""
import os
import sys
import uuid
import requests
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

# 加载环境变量
env_path = '/root/.openclaw/workspace/skills/vivago-ai-skill/.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

HIDREAM_TOKEN = os.environ.get('HIDREAM_TOKEN')
if not HIDREAM_TOKEN:
    print("❌ 错误: 未设置 HIDREAM_TOKEN 环境变量")
    sys.exit(1)

print("="*70)
print("新图片上传方式测试")
print("="*70)

# 配置
BASE_URL = "https://vivago.ai"
UPLOAD_ENDPOINT = "/prod-api/user/google_key/hidreamai-image"

# 生成唯一的文件名
image_uuid = f"j_{uuid.uuid4()}"
print(f"\n1. 准备上传")
print(f"   生成的图片 UUID: {image_uuid}")

# 步骤1: 获取预签名上传 URL
print(f"\n2. 获取预签名上传 URL...")
print(f"   GET {BASE_URL}{UPLOAD_ENDPOINT}")

headers = {
    "Authorization": f"Bearer {HIDREAM_TOKEN}",
    "Content-Type": "application/json"
}

params = {
    "filename": image_uuid,
    "content_type": "image/jpeg"
}

try:
    response = requests.get(
        f"{BASE_URL}{UPLOAD_ENDPOINT}",
        headers=headers,
        params=params,
        timeout=30
    )
    
    print(f"   响应状态码: {response.status_code}")
    print(f"   响应内容: {response.text[:200]}...")
    
    if response.status_code != 200:
        print(f"\n   ❌ 获取上传 URL 失败!")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        sys.exit(1)
    
    result = response.json()
    
    if result.get('code') != 0:
        print(f"\n   ❌ API 返回错误!")
        print(f"   Code: {result.get('code')}")
        print(f"   Message: {result.get('message')}")
        sys.exit(1)
    
    presigned_url = result.get('result')
    
    if not presigned_url:
        print(f"\n   ❌ 响应中未找到预签名 URL!")
        print(f"   完整响应: {result}")
        sys.exit(1)
    
    print(f"\n   ✅ 成功获取预签名 URL!")
    print(f"   URL 长度: {len(presigned_url)} 字符")
    print(f"   URL 预览: {presigned_url[:100]}...")
    
except Exception as e:
    print(f"\n   ❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步骤2: 使用预签名 URL 上传图片
print(f"\n3. 使用预签名 URL 上传图片...")
print(f"   PUT {presigned_url[:50]}...")

# 创建一个测试图片数据（简单的 JPEG）
# 为了测试，我们使用一个已有的测试图片或创建一个简单的图片
test_image_path = "/root/.openclaw/workspace/skills/vivago-ai-skill/tests/fixtures/images/portrait.jpg"

# 如果测试图片不存在，尝试找一个可用的图片
if not os.path.exists(test_image_path):
    # 尝试查找任何可用的图片
    possible_paths = [
        "/root/.openclaw/workspace/skills/vivago-ai-skill/assets/logo.jpg",
        "/root/.openclaw/workspace/test_image.jpg",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    else:
        print(f"   ⚠️  未找到测试图片，将创建一个简单的测试图片")
        # 创建一个简单的测试图片
        try:
            import numpy as np
            from PIL import Image
            
            # 创建一个 100x100 的红色图片
            img = Image.new('RGB', (100, 100), color='red')
            test_image_path = "/tmp/test_upload_image.jpg"
            img.save(test_image_path, 'JPEG', quality=80)
            print(f"   已创建测试图片: {test_image_path}")
        except Exception as e:
            print(f"   ❌ 创建测试图片失败: {e}")
            print(f"   请提供一个测试图片路径")
            sys.exit(1)

print(f"   测试图片路径: {test_image_path}")

try:
    # 读取图片二进制数据
    with open(test_image_path, 'rb') as f:
        image_data = f.read()
    
    print(f"   图片大小: {len(image_data)} bytes")
    
    # 使用 PUT 请求上传
    upload_response = requests.put(
        presigned_url,
        data=image_data,
        headers={
            "Content-Type": "image/jpeg"
        },
        timeout=60
    )
    
    print(f"   上传响应状态码: {upload_response.status_code}")
    
    if upload_response.status_code in [200, 201]:
        print(f"\n   ✅ 图片上传成功!")
        print(f"   上传的图片 UUID: {image_uuid}")
        print(f"\n   这个 UUID 可以用于后续的图片生成功能:")
        print(f"   - 图生图: image_to_image(image_uuids=['{image_uuid}'])")
        print(f"   - 图生视频: image_to_video(image_uuid='{image_uuid}')")
        print(f"   - 视频模板: template_to_video(image_uuid='{image_uuid}')")
    else:
        print(f"\n   ❌ 图片上传失败!")
        print(f"   状态码: {upload_response.status_code}")
        print(f"   响应: {upload_response.text[:500]}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n   ❌ 上传异常: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("测试完成!")
print("="*70)
print(f"\n新上传方式验证结果:")
print(f"  ✅ 获取预签名 URL: 成功")
print(f"  ✅ PUT 上传图片: 成功")
print(f"\n生成的图片 UUID: {image_uuid}")
print(f"\n结论: 新上传方式可行，可以替换现有实现")
