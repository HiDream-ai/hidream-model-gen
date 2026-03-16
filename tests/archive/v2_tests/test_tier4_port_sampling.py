#!/usr/bin/env python3
"""
Tier 4: 端口采样测试
中等API成本，按algo_type采样，同类端口只测代表
"""
import pytest
import sys
import os
import time
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vivago_client import create_client
from config_manager import get_config_manager
from fixtures.cache_manager import get_cache_manager, get_test_image_uuid, cache_test_result


# ============== 端口采样配置 ==============

# 按algo_type分组，每组只测1个代表端口
ALGO_TYPE_SAMPLES = {
    # 文生图
    "image_gen_kling": {
        "port": "kling-image",
        "test_method": "text_to_image",
        "params": {"prompt": "a simple circle", "batch_size": 1}
    },
    "txt2img": {
        "port": "hidream-txt2img",
        "test_method": "text_to_image",
        "params": {"prompt": "a simple circle", "batch_size": 1}
    },
    "image_gen_std": {
        "port": "nano-banana",
        "test_method": "text_to_image",
        "params": {"prompt": "a simple circle", "batch_size": 1}
    },
    
    # 图生视频
    "video_diffusion": {
        "port": "v3L",  # 代表v3L/v3Pro
        "test_method": "image_to_video",
        "params": {"prompt": "camera zoom", "duration": 5}
    },
    "video_diffusion_gen2vid": {
        "port": "kling-video",
        "test_method": "text_to_video",
        "params": {"prompt": "simple animation", "duration": 5}
    },
}


class TestTier4PortSampling:
    """
    Tier 4: 端口采样测试
    成本: ~¥5-10
    按algo_type采样，同类端口共享结果
    """
    
    @classmethod
    def setup_class(cls):
        """测试类准备"""
        cls.client = create_client()
        cls.cache = get_cache_manager()
        
        # 获取测试图片UUID
        cls.test_uuid = get_test_image_uuid("portrait")
        if not cls.test_uuid:
            pytest.skip("缺少测试图片UUID，请先运行Tier 2-3测试")
    
    def test_port_by_algo_type(self, algo_type: str, config: Dict):
        """测试指定algo_type的端口"""
        port = config["port"]
        test_method = config["test_method"]
        params = config["params"]
        
        print(f"\n🔌 测试端口: {port} (algo_type: {algo_type})")
        
        # 检查缓存
        cache_key = f"port_test_{port}"
        cached = self.cache.get_test_result(cache_key)
        if cached and not cached.get("invalidated"):
            print(f"   ℹ️  使用缓存结果: {cached['status']}")
            return cached
        
        try:
            # 执行测试
            if test_method == "text_to_image":
                result = self.client.text_to_image(
                    prompt=params["prompt"],
                    port=port,
                    batch_size=params["batch_size"]
                )
            elif test_method == "image_to_video":
                result = self.client.image_to_video(
                    prompt=params["prompt"],
                    image_uuid=self.test_uuid,
                    port=port,
                    duration=params["duration"]
                )
            elif test_method == "text_to_video":
                result = self.client.text_to_video(
                    prompt=params["prompt"],
                    port=port,
                    duration=params["duration"]
                )
            else:
                raise ValueError(f"Unknown test method: {test_method}")
            
            # 验证结果
            assert result is not None, f"端口 {port} 应该返回结果"
            
            # 缓存成功结果
            test_result = {
                "status": "success",
                "algo_type": algo_type,
                "port": port,
                "test_method": test_method
            }
            self.cache.save_test_result(cache_key, test_result)
            
            print(f"   ✅ 端口 {port} 测试成功")
            return test_result
            
        except Exception as e:
            # 记录失败
            error_msg = str(e)
            self.cache.record_failure("ports", port, error_msg)
            
            test_result = {
                "status": "failed",
                "algo_type": algo_type,
                "port": port,
                "error": error_msg
            }
            self.cache.save_test_result(cache_key, test_result)
            
            print(f"   ❌ 端口 {port} 测试失败: {error_msg}")
            return test_result
    
    def test_01_sample_all_algo_types(self):
        """采样测试所有algo_type"""
        print("\n" + "="*50)
        print("Tier 4: 端口采样测试")
        print("="*50)
        
        results = []
        
        for algo_type, config in ALGO_TYPE_SAMPLES.items():
            result = self.test_port_by_algo_type(algo_type, config)
            results.append(result)
            
            # 间隔等待，避免频率限制
            time.sleep(3)
        
        # 汇总结果
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = len(results) - success_count
        
        print(f"\n📊 采样测试完成:")
        print(f"   成功: {success_count}/{len(results)}")
        print(f"   失败: {failed_count}/{len(results)}")
        
        # 如果有失败，列出详情
        if failed_count > 0:
            print("\n❌ 失败端口:")
            for r in results:
                if r["status"] == "failed":
                    print(f"   - {r['port']}: {r.get('error', 'Unknown')}")
        
        # 保存汇总结果
        summary = {
            "tier": 4,
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }
        self.cache.save_test_result("tier4_summary", summary)
        
        # 断言至少大部分成功
        assert success_count >= len(results) * 0.7, f"至少70%端口应该成功"
    
    def test_02_retry_failed_ports(self):
        """重试之前失败的端口"""
        failed_ports = self.cache.get_failed_items("ports")
        
        if not failed_ports:
            print("\n✅ 没有失败的端口需要重试")
            return
        
        print(f"\n🔄 重试 {len(failed_ports)} 个失败的端口...")
        
        retry_success = []
        retry_failed = []
        
        for port in failed_ports[:3]:  # 最多重试3个
            # 查找对应的algo_type
            algo_type = None
            for at, cfg in ALGO_TYPE_SAMPLES.items():
                if cfg["port"] == port:
                    algo_type = at
                    break
            
            if algo_type:
                result = self.test_port_by_algo_type(algo_type, ALGO_TYPE_SAMPLES[algo_type])
                if result["status"] == "success":
                    retry_success.append(port)
                    # 清除失败记录
                    self.cache.clear_failure_record("ports", port)
                else:
                    retry_failed.append(port)
                
                time.sleep(3)
        
        print(f"\n📊 重试结果:")
        print(f"   成功恢复: {len(retry_success)}")
        print(f"   仍然失败: {len(retry_failed)}")


# ============== 成本估算 ==============

def estimate_tier4_cost():
    """估算Tier 4测试成本"""
    costs = {
        "kling-image": 0.1,       # 文生图
        "hidream-txt2img": 0.1,   # 文生图
        "nano-banana": 0.1,       # 文生图
        "v3L": 0.5,               # 图生视频
        "kling-video": 0.5,       # 文生视频
    }
    total = sum(costs.values())
    print(f"\n💰 Tier 4 测试预估成本: ¥{total:.1f}")
    print(f"   基于 {len(ALGO_TYPE_SAMPLES)} 个代表端口")
    return total


if __name__ == '__main__':
    estimate_tier4_cost()
    
    print("\n" + "="*50)
    print("开始运行 Tier 4 端口采样测试...")
    print("="*50 + "\n")
    
    pytest.main([__file__, '-v', '-s'])
