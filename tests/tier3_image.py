#!/usr/bin/env python3
"""
Tier 3: 核心功能冒烟测试
图片功能: 16积分 (文生图 + 图生图)
"""
import os
from scripts.vivago_client import create_client

print("="*60)
print("Tier 3: 核心功能冒烟测试")
print("预估积分: 16 (图片功能)")
print("="*60)

client = create_client()
results = []

# Test 1: 文生图 (Kling O1) - 8积分
print("\n🎨 Test 1: 文生图 (Kling O1) - 8积分")
print("⏳ 生成中...")
try:
    result = client.text_to_image(
        prompt='a cute cartoon cat, colorful and cheerful',
        port='kling-image',
        batch_size=1,
        wh_ratio='1:1'
    )
    
    if result and len(result) > 0:
        print(f"✅ 成功! 图片ID: {result[0].get('image', 'N/A')[:30]}...")
        results.append(("文生图 (Kling O1)", "✅ 通过", 8))
    else:
        results.append(("文生图 (Kling O1)", "❌ 失败: 无结果", 0))
except Exception as e:
    print(f"❌ 失败: {e}")
    results.append(("文生图 (Kling O1)", f"❌ 失败: {e}", 0))

# Test 2: 图生图 (Kling O1) - 8积分
print("\n🔄 Test 2: 图生图 (Kling O1) - 8积分")
print("⏳ 生成中...")
try:
    # 使用已有的logo图片
    image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"
    
    result = client.image_to_image(
        prompt='convert to watercolor painting style',
        image_uuids=[image_uuid],
        port='kling-image',
        strength=0.7
    )
    
    if result and len(result) > 0:
        print(f"✅ 成功! 图片ID: {result[0].get('image', 'N/A')[:30]}...")
        results.append(("图生图 (Kling O1)", "✅ 通过", 8))
    else:
        results.append(("图生图 (Kling O1)", "❌ 失败: 无结果", 0))
except Exception as e:
    print(f"❌ 失败: {e}")
    results.append(("图生图 (Kling O1)", f"❌ 失败: {e}", 0))

# 打印汇总
print("\n" + "="*60)
total_credits = sum(c for _, _, c in results)
passed = sum(1 for _, r, _ in results if "✅" in r)

for name, status, credits in results:
    print(f"{name:.<30} {status}")

print("-"*60)
print(f"结果: {passed}/{len(results)} 通过")
print(f"积分消耗: {total_credits}")
print("="*60)

if passed == len(results):
    print("✅ Tier 3 Phase 1 (图片功能) 通过!")
    print("\n下一步: 运行视频功能测试 (单独执行):")
    print("  - tests/tier3_phase2_video.py")
else:
    print(f"⚠️  {len(results) - passed} 项失败")
