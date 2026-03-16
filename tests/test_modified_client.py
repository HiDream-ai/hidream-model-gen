#!/usr/bin/env python3
"""
测试修改后的 vivago_client.py
验证新方法 upload_image_v2 和修改后的 upload_image
"""
import os
import sys
import warnings

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from scripts.vivago_client import create_client

print("="*70)
print("测试修改后的 vivago_client.py")
print("="*70)

client = create_client()

# 测试图片路径
test_image = "/root/.openclaw/workspace/skills/vivago-ai-skill/tests/fixtures/images/portrait.jpg"

print("\n1. 测试 upload_image() - 现在应该使用 v2 方式")
print("-"*70)
try:
    uuid1 = client.upload_image(test_image)
    print(f"✅ upload_image() 成功!")
    print(f"   UUID: {uuid1}")
except Exception as e:
    print(f"❌ upload_image() 失败: {e}")

print("\n2. 测试 upload_image_v2() - 明确调用 v2 方式")
print("-"*70)
try:
    uuid2 = client.upload_image_v2(test_image)
    print(f"✅ upload_image_v2() 成功!")
    print(f"   UUID: {uuid2}")
except Exception as e:
    print(f"❌ upload_image_v2() 失败: {e}")

print("\n3. 测试 upload_image_legacy() - 应该触发 DeprecationWarning")
print("-"*70)
# 捕获警告信息
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    try:
        uuid3 = client.upload_image_legacy(test_image)
        print(f"✅ upload_image_legacy() 成功!")
        print(f"   UUID: {uuid3}")
    except Exception as e:
        print(f"❌ upload_image_legacy() 失败: {e}")
    
    # 检查是否有 DeprecationWarning
    if w:
        for warning in w:
            if issubclass(warning.category, DeprecationWarning):
                print(f"\n⚠️  DeprecationWarning 触发成功!")
                print(f"   消息: {warning.message}")
    else:
        print("\n⚠️  警告: 未触发 DeprecationWarning")

print("\n" + "="*70)
print("测试完成!")
print("="*70)
