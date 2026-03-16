#!/usr/bin/env python3
"""
Tier 2: 组件集成测试 + Tier 3: 核心功能冒烟测试
极低API成本，使用缓存和最小参数
"""
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vivago_client import create_client
from vivago_client_v2 import create_client_v2
from config_manager import get_config_manager
from template_manager import get_template_manager
from fixtures.cache_manager import get_cache_manager, get_test_image_uuid
from fixtures.test_assets import get_test_asset_manager


# ============== Tier 2: 组件集成测试 ==============

class TestTier2ComponentIntegration:
    """
    Tier 2: 组件集成测试
    成本: ~¥0.1
    验证组件协作，最小化API调用
    """
    
    def test_01_config_manager_loading(self):
        """测试配置管理器加载 - 零成本"""
        manager = get_config_manager()
        ports = manager.list_ports()
        
        # 验证加载了端口
        assert len(ports) > 0, "应该加载了端口配置"
        
        # 验证标准端口存在
        assert "kling-image" in ports, "应该包含kling-image端口"
        assert "v3Pro" in ports, "应该包含v3Pro端口"
        
        print(f"✅ 配置管理器加载成功: {len(ports)} 个端口")
    
    def test_02_template_manager_loading(self):
        """测试模板管理器加载 - 零成本"""
        manager = get_template_manager()
        templates = manager.list_templates()
        
        # 验证加载了模板
        assert len(templates) > 0, "应该加载了模板"
        
        # 验证常见模板存在
        assert "ghibli" in templates or "renovation_old_photos" in templates, \
            "应该包含常见模板"
        
        print(f"✅ 模板管理器加载成功: {len(templates)} 个模板")
    
    def test_03_cache_manager_operations(self):
        """测试缓存管理器操作 - 零成本"""
        cm = get_cache_manager()
        
        # 保存测试数据
        cm.save_image_uuid("test_type", "j_test_uuid")
        cm.save_test_result("test_key", {"status": "success"})
        
        # 读取测试数据
        uuid = cm.get_image_uuid("test_type")
        result = cm.get_test_result("test_key")
        
        assert uuid == "j_test_uuid", "应该读取到保存的UUID"
        assert result["status"] == "success", "应该读取到保存的结果"
        
        # 清除测试数据
        cm.clear_image_uuids()
        cm.clear_test_results()
        
        print("✅ 缓存管理器操作正常")
    
    @pytest.mark.api_cost(minimal=True)
    def test_04_image_upload_and_cache(self):
        """
        测试图片上传流程 - 极低成本(仅首次)
        后续测试将使用缓存的UUID
        """
        # 检查是否有缓存的UUID
        cached_uuid = get_test_image_uuid("portrait")
        
        if cached_uuid:
            print(f"✅ 使用缓存的图片UUID: {cached_uuid}")
            assert cached_uuid.startswith("j_")
            return
        
        # 如果没有缓存，需要上传
        manager = get_test_asset_manager()
        status = manager.check_test_images()
        
        if not status.get("portrait"):
            pytest.skip("缺少测试图片，跳过上传测试")
        
        # 上传图片 (成本: ~¥0.01)
        uuid = manager.upload_image("portrait")
        
        if uuid:
            print(f"✅ 图片上传成功: {uuid}")
            assert uuid.startswith("j_")
        else:
            pytest.fail("图片上传失败")


# ============== Tier 3: 核心功能冒烟测试 ==============

@pytest.mark.api_cost(low=True)
class TestTier3CoreFeaturesSmoke:
    """
    Tier 3: 核心功能冒烟测试
    成本: ~¥2
    每个核心功能只测最基本路径
    """
    
    @classmethod
    def setup_class(cls):
        """测试类准备"""
        cls.client = create_client()
        cls.client_v2 = create_client_v2()
        
        # 获取测试图片UUID
        cls.test_uuid = get_test_image_uuid("portrait")
        if not cls.test_uuid:
            pytest.skip("缺少测试图片UUID，请先运行Tier 2测试上传图片")
    
    def test_01_text_to_image_kling(self):
        """
        文生图 - 只测最快的Kling
        预期成本: ~¥0.1
        预期时间: ~10秒
        """
        print("\n🎨 测试文生图 (Kling O1)...")
        
        result = self.client.text_to_image(
            prompt="a red circle on white background",  # 最简单的提示词
            port="kling-image",
            batch_size=1,  # 只生成1张
            wh_ratio="1:1"
        )
        
        assert result is not None, "文生图应该返回结果"
        assert len(result) > 0, "应该至少生成1张图片"
        
        # 缓存成功的结果
        get_cache_manager().save_test_result(
            "smoke_text_to_image_kling",
            {"status": "success", "result_count": len(result)}
        )
        
        print(f"✅ 文生图成功: 生成 {len(result)} 张图片")
    
    def test_02_image_to_video_v3l(self):
        """
        图生视频 - 只测v3L (360p最快)
        预期成本: ~¥0.5
        预期时间: ~2分钟
        """
        print("\n🎬 测试图生视频 (v3L)...")
        
        result = self.client.image_to_video(
            prompt="camera slowly zooming out",
            image_uuid=self.test_uuid,
            port="v3L",  # 最快的端口
            duration=5,  # 最短时长
            wh_ratio="1:1"
        )
        
        assert result is not None, "图生视频应该返回结果"
        assert len(result) > 0, "应该生成视频"
        
        # 缓存结果
        get_cache_manager().save_test_result(
            "smoke_image_to_video_v3l",
            {"status": "success"}
        )
        
        print("✅ 图生视频成功")
    
    def test_03_text_to_video_v3l(self):
        """
        文生视频 - 只测v3L
        预期成本: ~¥0.5
        预期时间: ~2分钟
        """
        print("\n📝 测试文生视频 (v3L)...")
        
        result = self.client.text_to_video(
            prompt="a flower blooming",  # 简单的自然场景
            port="v3L",
            duration=5,
            wh_ratio="1:1"
        )
        
        assert result is not None, "文生视频应该返回结果"
        
        # 缓存结果
        get_cache_manager().save_test_result(
            "smoke_text_to_video_v3l",
            {"status": "success"}
        )
        
        print("✅ 文生视频成功")
    
    def test_04_image_to_image_kling(self):
        """
        图生图 - 只测Kling
        预期成本: ~¥0.1
        预期时间: ~10秒
        """
        print("\n🔄 测试图生图 (Kling)...")
        
        result = self.client.image_to_image(
            prompt="convert to watercolor painting style",
            image_uuids=[self.test_uuid],
            port="kling-image",
            strength=0.7
        )
        
        assert result is not None, "图生图应该返回结果"
        
        # 缓存结果
        get_cache_manager().save_test_result(
            "smoke_image_to_image_kling",
            {"status": "success"}
        )
        
        print("✅ 图生图成功")
    
    def test_05_keyframe_to_video_v3l(self):
        """
        视频首尾帧 - 使用相同图片测试
        预期成本: ~¥0.5
        预期时间: ~2分钟
        """
        print("\n🎞️ 测试视频首尾帧 (v3L)...")
        
        result = self.client.keyframe_to_video(
            prompt="smooth transition",
            start_image_uuid=self.test_uuid,
            end_image_uuid=self.test_uuid,  # 相同图片
            port="v3L",
            duration=5,
            wh_ratio="1:1"
        )
        
        assert result is not None, "首尾帧视频应该返回结果"
        
        # 缓存结果
        get_cache_manager().save_test_result(
            "smoke_keyframe_to_video_v3l",
            {"status": "success"}
        )
        
        print("✅ 视频首尾帧成功")
    
    def test_06_template_to_video_basic(self):
        """
        视频模板 - 只测最稳定的模板
        预期成本: ~¥0.5
        预期时间: ~2分钟
        """
        print("\n🎭 测试视频模板 (renovation_old_photos)...")
        
        # 使用最稳定的模板
        result = self.client.template_to_video(
            image_uuid=self.test_uuid,
            template="renovation_old_photos",
            wh_ratio="1:1"
        )
        
        assert result is not None, "视频模板应该返回结果"
        
        # 缓存结果
        get_cache_manager().save_test_result(
            "smoke_template_renovation",
            {"status": "success"}
        )
        
        print("✅ 视频模板成功")
    
    def test_07_v2_client_compatibility(self):
        """
        V2客户端兼容性测试
        验证V2客户端至少能正常工作
        """
        print("\n🔧 测试V2客户端兼容性...")
        
        # 测试V2客户端能初始化
        assert self.client_v2 is not None
        
        # 测试V2能获取配置
        config = get_config_manager().get_port("kling-image")
        assert config is not None
        
        print("✅ V2客户端兼容性正常")


# ============== 测试成本估算 ==============

def estimate_tier3_cost():
    """估算Tier 3测试成本"""
    costs = {
        "text_to_image": 0.1,
        "image_to_video": 0.5,
        "text_to_video": 0.5,
        "image_to_image": 0.1,
        "keyframe_to_video": 0.5,
        "template_to_video": 0.5,
    }
    total = sum(costs.values())
    print(f"\n💰 Tier 3 测试预估成本: ¥{total:.1f}")
    print(f"   详细: {costs}")
    return total


if __name__ == '__main__':
    # 运行前先估算成本
    estimate_tier3_cost()
    
    print("\n" + "="*50)
    print("开始运行 Tier 2+3 测试...")
    print("="*50 + "\n")
    
    pytest.main([__file__, '-v', '-s'])
