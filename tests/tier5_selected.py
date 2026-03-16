#!/usr/bin/env python3
"""
Tier 5: 模板采样测试 (精选)
选择5个代表性模板，150积分
"""
import sys
import os

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from vivago_client import create_client

print("="*60)
print("Tier 5: 模板采样测试 (精选)")
print("选择5个代表性模板")
print("预估积分: 150")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"
print(f"✅ 使用测试图片: {image_uuid}")

# 选择5个代表性模板
templates = [
    ("ghibli", "Ghibli风格"),
    ("iron_man", "钢铁侠"),
    ("magic_reveal_ravenclaw", "哈利波特-拉文克劳"),
    ("angel_wings", "天使翅膀"),
    ("barbie", "芭比风格")
]

results = []

for i, (template_id, name) in enumerate(templates, 1):
    print(f"\n🎭 [{i}/5] {name} ({template_id}) - 30积分")
    print("   ⏳ 生成中...")
    
    try:
        result = client.template_to_video(
            image_uuid=image_uuid,
            template=template_id,
            wh_ratio='9:16'
        )
        
        if result:
            print(f"   ✅ {name} 成功!")
            results.append((name, "✅ 通过", 30))
        else:
            print(f"   ❌ {name} 失败")
            results.append((name, "❌ 失败", 0))
    except Exception as e:
        print(f"   ❌ {name} 错误: {str(e)[:50]}")
        results.append((name, f"❌ 错误", 0))

# 打印汇总
print("\n" + "="*60)
total_credits = sum(c for _, _, c in results)
passed = sum(1 for _, r, _ in results if "✅" in r)

for name, status, credits in results:
    print(f"{name:.<20} {status}")

print("-"*60)
print(f"结果: {passed}/{len(results)} 通过")
print(f"积分消耗: {total_credits}")
print("="*60)

if passed == len(results):
    print("✅ Tier 5 模板测试全部通过!")
else:
    print(f"⚠️  {len(results) - passed} 项失败")
