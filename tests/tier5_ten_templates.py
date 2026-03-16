#!/usr/bin/env python3
"""
Tier 5: 模板采样测试 (10个精选模板)
预估积分: 300
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
from fixtures.cache_manager import get_cache_manager

print("="*60)
print("Tier 5: 模板采样测试 (10个精选模板)")
print("预估积分: 300 (30×10)")
print("="*60)

client = create_client()
cache = get_cache_manager()
test_uuid = cache.get_image_uuid('portrait')

if not test_uuid:
    print('❌ 请先运行 tier3_phase1_image.py 上传测试图片')
    sys.exit(1)

print(f'✅ 使用测试图片: {test_uuid}')

# 10个精选模板（包含不同类别）
templates = [
    ("ghibli", "Ghibli风格", "动漫风格"),
    ("iron_man", "钢铁侠", "超级英雄"),
    ("magic_reveal_ravenclaw", "哈利波特-拉文克劳", "魔法学院"),
    ("angel_wings", "天使翅膀", "翅膀特效"),
    ("barbie", "芭比风格", "风格转换"),
    ("apt", "APT舞蹈", "舞蹈模板"),
    ("flash_flood", "洪水特效", "特效类"),
    ("cat_woman", "猫女", "超级英雄"),
    ("mermaid", "美人鱼", "奇幻场景"),
    ("graduation", "毕业典礼", "场景类"),
]

results = []

for i, (template_id, name, category) in enumerate(templates, 1):
    print(f"\n🎭 [{i}/10] {name} ({template_id})")
    print(f"   类别: {category} | 积分: 30")
    print("   ⏳ 生成中...")
    
    try:
        result = client.template_to_video(
            image_uuid=test_uuid,
            template=template_id,
            wh_ratio='9:16'
        )
        
        if result:
            print(f"   ✅ {name} 成功!")
            results.append((name, template_id, "✅ 通过", 30, category))
            # 保存成功结果
            cache.save_test_result(f'tier5_template_{template_id}', {
                'status': 'success',
                'name': name,
                'category': category
            })
        else:
            print(f"   ❌ {name} 失败: 无结果")
            results.append((name, template_id, "❌ 失败", 0, category))
    except Exception as e:
        print(f"   ❌ {name} 错误: {str(e)[:60]}")
        results.append((name, template_id, f"❌ 错误", 0, category))

# 打印汇总
print("\n" + "="*60)
print("Tier 5 模板测试完成")
print("="*60)

total_credits = sum(c for _, _, _, c, _ in results)
passed = sum(1 for _, _, r, _, _ in results if "✅" in r)
failed = sum(1 for _, _, r, _, _ in results if "❌" in r)

print("\n📊 测试结果汇总:")
print("-"*60)
for name, template_id, status, credits, category in results:
    print(f"{name:.<15} {template_id:.<25} {status}")

print("-"*60)
print(f"✅ 通过: {passed}/{len(results)}")
print(f"❌ 失败: {failed}/{len(results)}")
print(f"💰 积分消耗: {total_credits}")
print("="*60)

# 按类别统计
print("\n📂 按类别统计:")
categories = {}
for _, _, status, _, category in results:
    if category not in categories:
        categories[category] = {'total': 0, 'passed': 0}
    categories[category]['total'] += 1
    if "✅" in status:
        categories[category]['passed'] += 1

for cat, stats in categories.items():
    print(f"   {cat}: {stats['passed']}/{stats['total']} 通过")

if passed == len(results):
    print("\n🎉 Tier 5 模板测试全部通过!")
elif passed >= 8:
    print(f"\n✅ Tier 5 测试通过 (通过率 {passed}/{len(results)})")
else:
    print(f"\n⚠️  测试通过率较低 ({passed}/{len(results)})，建议检查失败模板")

# 保存汇总结果
cache.save_test_result('tier5_summary', {
    'total': len(results),
    'passed': passed,
    'failed': failed,
    'credits': total_credits,
    'templates': [t[1] for t in results],
    'failed_templates': [t[1] for t in results if "❌" in t[2]]
})
