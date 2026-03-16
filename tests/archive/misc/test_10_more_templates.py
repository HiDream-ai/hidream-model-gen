#!/usr/bin/env python3
"""
Tier 5: 再补充测试10种视频模板
预估积分: 300 (30 x 10)
选择未测试过的类别
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
print("Tier 5: 再补充测试10种视频模板")
print("预估积分: 300 (30 x 10)")
print("="*60)

client = create_client()
image_uuid = "j_4df35382-a312-48e6-9b78-1117e7c1be6d"
print(f"✅ 使用测试图片: {image_uuid}")

# 选择10个不同类型且未测试过的模板
templates = [
    ("dance", "舞蹈", "9:16"),
    ("limbo_dance", "Limbo舞蹈", "9:16"),
    ("magic_reveal_gryffindor", "格兰芬多", "9:16"),
    ("joker", "小丑", "9:16"),
    ("mermaid", "美人鱼", "9:16"),
    ("metallic_liquid", "金属液体", "9:16"),
    ("eye_of_the_storm", "风暴之眼", "9:16"),
    ("autumn_feast", "感恩节盛宴", "9:16"),
    ("ai_archaeologist", "AI考古学家", "9:16"),
    ("starship_chef", "星舰厨师", "9:16")
]

results = []

for i, (template_id, name, ratio) in enumerate(templates, 1):
    print(f"\n🎭 [{i}/10] {name} ({template_id}) - 30积分")
    print("   ⏳ 生成中...")
    
    try:
        result = client.template_to_video(
            image_uuid=image_uuid,
            template=template_id,
            wh_ratio=ratio
        )
        
        if result and len(result) > 0:
            video_id = result[0].get('video', 'N/A')
            print(f"   ✅ {name} 成功!")
            print(f"      视频ID: {video_id}")
            results.append((name, "✅ 通过", 30))
        else:
            print(f"   ❌ {name} 失败: 无结果")
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
    print("✅ 所有模板测试通过!")
else:
    print(f"⚠️  {len(results) - passed} 项失败")
