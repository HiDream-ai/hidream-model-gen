#!/usr/bin/env python3
"""
Tier 5: 模板智能采样测试
高API成本，分类采样 + 增量测试
"""
import pytest
import sys
import os
import time
from typing import List, Dict, Set

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vivago_client import create_client
from template_manager import get_template_manager
from fixtures.cache_manager import get_cache_manager, get_test_image_uuid


# ============== 模板分类采样配置 ==============

# 按功能类别采样，每类只测1-2个代表
TEMPLATE_CATEGORY_SAMPLES = {
    "style_transfer": ["ghibli"],
    "harry_potter": ["magic_reveal_ravenclaw"],  # 只测1个学院
    "wings": ["angel_wings", "phoenix_wings"],
    "superhero": ["iron_man"],
    "dance": ["apt"],
    "thanksgiving": ["turkey_chasing"],  # 只测1个火鸡模板
    "effects": ["ash_out"],
    "comics": ["gta_star"],
    "products": ["glasses_display"],
    "scenes": ["romantic_kiss"],
    "transform": ["barbie"],
    "photo_restore": ["renovation_old_photos"],
}

# 所有采样模板
ALL_SAMPLE_TEMPLATES = []
for templates in TEMPLATE_CATEGORY_SAMPLES.values():
    ALL_SAMPLE_TEMPLATES.extend(templates)


class TestTier5TemplateSampling:
    """
    Tier 5: 模板智能采样测试
    成本: ~¥20-40 (约40个模板)
    策略: 分类采样 + 失败优先 + 缓存复用
    """
    
    @classmethod
    def setup_class(cls):
        """测试类准备"""
        cls.client = create_client()
        cls.cache = get_cache_manager()
        cls.template_manager = get_template_manager()
        
        # 获取测试图片UUID
        cls.test_uuid = get_test_image_uuid("portrait")
        if not cls.test_uuid:
            pytest.skip("缺少测试图片UUID，请先运行Tier 2-3测试")
    
    def get_templates_to_test(self) -> List[str]:
        """确定需要测试的模板列表"""
        templates_to_test = []
        
        # 1. 上次失败的模板 (优先)
        failed_templates = self.cache.get_failed_items("templates")
        for template in failed_templates:
            if template in ALL_SAMPLE_TEMPLATES:
                templates_to_test.append(template)
                print(f"   🔄 失败模板优先: {template}")
        
        # 2. 采样的模板 (去重)
        for template in ALL_SAMPLE_TEMPLATES:
            if template not in templates_to_test:
                # 检查是否已有有效缓存
                cache_key = f"template_test_{template}"
                cached = self.cache.get_test_result(cache_key)
                
                if cached and cached.get("status") == "success":
                    print(f"   ℹ️  跳过已测试: {template}")
                    continue
                
                templates_to_test.append(template)
        
        return templates_to_test
    
    def test_single_template(self, template_id: str) -> Dict:
        """测试单个模板"""
        # 检查模板是否存在
        template = self.template_manager.get_template(template_id)
        if not template:
            return {
                "template": template_id,
                "status": "skipped",
                "reason": "Template not found"
            }
        
        print(f"\n🎭 测试模板: {template_id}")
        
        try:
            # 执行测试
            result = self.client.template_to_video(
                image_uuid=self.test_uuid,
                template=template_id,
                wh_ratio="1:1"
            )
            
            assert result is not None, "模板应该返回结果"
            
            # 确定结果类型
            result_urls = result.get('result', [])
            result_type = "video" if any('.mp4' in str(url) for url in result_urls) else "image"
            
            # 保存成功结果
            test_result = {
                "template": template_id,
                "status": "success",
                "result_type": result_type,
                "name": template.get('name', template_id)
            }
            
            # 清除失败记录
            self.cache.clear_failure_record("templates", template_id)
            
            print(f"   ✅ 成功 ({result_type})")
            return test_result
            
        except Exception as e:
            error_msg = str(e)
            
            # 记录失败
            self.cache.record_failure("templates", template_id, error_msg)
            
            test_result = {
                "template": template_id,
                "status": "failed",
                "error": error_msg,
                "name": template.get('name', template_id) if template else template_id
            }
            
            print(f"   ❌ 失败: {error_msg[:50]}...")
            return test_result
    
    def test_01_sample_templates(self):
        """采样测试模板"""
        print("\n" + "="*50)
        print("Tier 5: 模板智能采样测试")
        print("="*50)
        
        templates = self.get_templates_to_test()
        
        if not templates:
            print("\n✅ 所有模板已有有效缓存，无需测试")
            return
        
        print(f"\n📋 计划测试 {len(templates)} 个模板:")
        print(f"   {templates}")
        
        # 估算成本
        estimated_cost = len(templates) * 0.5  # 每个模板约¥0.5
        print(f"\n💰 预估成本: ¥{estimated_cost:.1f}")
        
        # 执行测试
        results = []
        for i, template in enumerate(templates, 1):
            print(f"\n[{i}/{len(templates)}] ", end="")
            result = self.test_single_template(template)
            results.append(result)
            
            # 保存结果到缓存
            cache_key = f"template_test_{template}"
            self.cache.save_test_result(cache_key, result)
            
            # 间隔等待
            if i < len(templates):
                time.sleep(5)
        
        # 汇总
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        skipped_count = sum(1 for r in results if r["status"] == "skipped")
        
        print(f"\n\n📊 模板测试完成:")
        print(f"   总数: {len(results)}")
        print(f"   成功: {success_count} ✅")
        print(f"   失败: {failed_count} ❌")
        print(f"   跳过: {skipped_count} ⏭️")
        
        # 按类别汇总
        print(f"\n📂 按类别汇总:")
        for category, cat_templates in TEMPLATE_CATEGORY_SAMPLES.items():
            cat_results = [r for r in results if r["template"] in cat_templates]
            cat_success = sum(1 for r in cat_results if r["status"] == "success")
            print(f"   {category}: {cat_success}/{len(cat_templates)} 成功")
        
        # 保存汇总
        summary = {
            "tier": 5,
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "templates_tested": [r["template"] for r in results],
            "failed_templates": [r["template"] for r in results if r["status"] == "failed"]
        }
        self.cache.save_test_result("tier5_summary", summary)
        
        # 输出失败详情
        if failed_count > 0:
            print(f"\n❌ 失败的模板:")
            for r in results:
                if r["status"] == "failed":
                    print(f"   - {r['template']}: {r.get('error', 'Unknown')[:50]}...")
        
        # 断言成功率
        success_rate = success_count / len([r for r in results if r["status"] != "skipped"])
        assert success_rate >= 0.7, f"模板成功率应 >= 70%，实际 {success_rate*100:.1f}%"
    
    def test_02_new_templates_detection(self):
        """检测新增/修改的模板"""
        all_templates = self.template_manager.list_templates()
        
        # 找出不在采样列表中的模板
        unsampled = [t for t in all_templates.keys() if t not in ALL_SAMPLE_TEMPLATES]
        
        print(f"\n📊 模板统计:")
        print(f"   总模板数: {len(all_templates)}")
        print(f"   采样测试: {len(ALL_SAMPLE_TEMPLATES)}")
        print(f"   未采样: {len(unsampled)}")
        
        if unsampled:
            print(f"\n💡 未采样的模板（可考虑加入采样列表）:")
            for t in unsampled[:10]:  # 最多显示10个
                print(f"   - {t}")


# ============== 便捷测试函数 ==============

def test_specific_template(template_id: str):
    """便捷函数：测试特定模板"""
    client = create_client()
    cache = get_cache_manager()
    test_uuid = get_test_image_uuid("portrait")
    
    if not test_uuid:
        print("❌ 缺少测试图片UUID")
        return
    
    print(f"\n🎭 测试特定模板: {template_id}")
    
    try:
        result = client.template_to_video(
            image_uuid=test_uuid,
            template=template_id,
            wh_ratio="1:1"
        )
        
        cache.save_test_result(f"template_test_{template_id}", {
            "template": template_id,
            "status": "success"
        })
        
        print(f"✅ 模板 {template_id} 测试成功")
        return True
        
    except Exception as e:
        cache.record_failure("templates", template_id, str(e))
        print(f"❌ 模板 {template_id} 测试失败: {e}")
        return False


if __name__ == '__main__':
    print(f"\n💰 Tier 5 测试预估成本: ¥{len(ALL_SAMPLE_TEMPLATES) * 0.5:.1f}")
    print(f"   采样模板数: {len(ALL_SAMPLE_TEMPLATES)}")
    
    print("\n" + "="*50)
    print("开始运行 Tier 5 模板采样测试...")
    print("="*50 + "\n")
    
    pytest.main([__file__, '-v', '-s'])
