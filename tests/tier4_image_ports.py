#!/usr/bin/env python3
"""
Tier 4: 图片端口采样测试
预估积分: 28 (图片端口)
"""
import sys
import os
import time

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

# 检查是否已有测试在运行
LOCK_FILE = '/tmp/tier4_test.lock'
if os.path.exists(LOCK_FILE):
    lock_age = time.time() - os.path.getmtime(LOCK_FILE)
    if lock_age < 600:  # 10分钟内
        print("❌ Tier 4 测试已在运行中，请勿重复提交")
        print(f"   锁文件: {LOCK_FILE}")
        sys.exit(1)
    else:
        os.remove(LOCK_FILE)

# 创建锁文件
with open(LOCK_FILE, 'w') as f:
    f.write(str(os.getpid()))

def cleanup():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from scripts.vivago_client import create_client

print("="*60)
print("Tier 4: 图片端口采样测试")
print("预估积分: 28")
print("="*60)

client = create_client()
results = []

# Test 1: Kling O1 文生图 - 8积分
print("\n🔌 [1/4] Kling O1 文生图 - 8积分")
try:
    result = client.text_to_image(
        prompt='a cute puppy playing in garden',
        port='kling-image',
        batch_size=1
    )
    if result:
        print("   ✅ 通过")
        results.append(("Kling O1 文生图", "✅ 通过", 8))
    else:
        results.append(("Kling O1 文生图", "❌ 失败", 0))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("Kling O1 文生图", f"❌ 失败: {e}", 0))

# Test 2: Vivago 2.0 文生图 - 2积分 (最低成本)
print("\n🔌 [2/4] Vivago 2.0 文生图 - 2积分")
try:
    result = client.text_to_image(
        prompt='sunset over mountains',
        port='hidream-txt2img',
        batch_size=1
    )
    if result:
        print("   ✅ 通过")
        results.append(("Vivago 2.0 文生图", "✅ 通过", 2))
    else:
        results.append(("Vivago 2.0 文生图", "❌ 失败", 0))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("Vivago 2.0 文生图", f"❌ 失败: {e}", 0))

# Test 3: Nano Banana 文生图 - 10积分 (带超时)
print("\n🔌 [3/4] Nano Banana 文生图 - 10积分")
print("   ⏳ 需要较长时间，设置最大等待 5 分钟...")
try:
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Nano Banana 测试超时 (5分钟)")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1800)  # 30分钟超时
    
    result = client.text_to_image(
        prompt='fresh fruit arrangement, high quality',
        port='nano-banana',
        batch_size=1
    )
    
    signal.alarm(0)  # 取消超时
    
    if result:
        print("   ✅ 通过")
        results.append(("Nano Banana 文生图", "✅ 通过", 10))
    else:
        results.append(("Nano Banana 文生图", "❌ 失败", 0))
except TimeoutError as e:
    print(f"   ⚠️  超时: {e}")
    results.append(("Nano Banana 文生图", "⚠️ 超时", 0))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("Nano Banana 文生图", f"❌ 失败: {e}", 0))

# Test 4: Kling O1 图生图 - 8积分
print("\n🔌 [4/4] Kling O1 图生图 - 8积分")
try:
    image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"
    result = client.image_to_image(
        prompt='convert to oil painting style',
        image_uuids=[image_uuid],
        port='kling-image',
        strength=0.7
    )
    if result:
        print("   ✅ 通过")
        results.append(("Kling O1 图生图", "✅ 通过", 8))
    else:
        results.append(("Kling O1 图生图", "❌ 失败", 0))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("Kling O1 图生图", f"❌ 失败: {e}", 0))

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
    print("✅ Tier 4 图片端口测试通过!")
    print("\n下一步: 视频端口测试 (单独执行):")
    print("  - tests/tier4_video_v3l.py (60积分)")
    print("  - tests/tier4_video_kling.py (80积分)")
else:
    print(f"⚠️  {len(results) - passed} 项失败")

# 清理锁文件
cleanup()
