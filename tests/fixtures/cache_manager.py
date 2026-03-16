#!/usr/bin/env python3
"""
测试缓存管理器
支持持久化缓存，手动清除
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class TestCacheManager:
    """
    持久化测试缓存管理器
    
    缓存策略:
    - 测试图片UUID: 永久有效，手动清除
    - 测试结果: 永久有效，手动标记失效
    - 失败记录: 永久保留，优先重测
    """
    
    CACHE_DIR = Path(__file__).parent / "cache"
    
    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.uuids_file = self.CACHE_DIR / "uuids.json"
        self.results_file = self.CACHE_DIR / "test_results.json"
        self.failures_file = self.CACHE_DIR / "failed_items.json"
    
    # ========== 图片UUID缓存 (永久) ==========
    
    def get_image_uuid(self, image_type: str) -> Optional[str]:
        """获取缓存的图片UUID"""
        if not self.uuids_file.exists():
            return None
        with open(self.uuids_file, 'r', encoding='utf-8') as f:
            uuids = json.load(f)
        return uuids.get(image_type)
    
    def save_image_uuid(self, image_type: str, uuid: str):
        """保存图片UUID到缓存"""
        uuids = {}
        if self.uuids_file.exists():
            with open(self.uuids_file, 'r', encoding='utf-8') as f:
                uuids = json.load(f)
        uuids[image_type] = uuid
        with open(self.uuids_file, 'w', encoding='utf-8') as f:
            json.dump(uuids, f, indent=2)
    
    def list_cached_images(self) -> Dict[str, str]:
        """列出所有缓存的图片UUID"""
        if not self.uuids_file.exists():
            return {}
        with open(self.uuids_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clear_image_uuids(self) -> bool:
        """清除图片UUID缓存 - 需要重新上传"""
        if self.uuids_file.exists():
            self.uuids_file.unlink()
            return True
        return False
    
    # ========== 测试结果缓存 (永久，手动失效) ==========
    
    def get_test_result(self, test_key: str) -> Optional[Dict]:
        """获取缓存的测试结果"""
        if not self.results_file.exists():
            return None
        with open(self.results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        result = results.get(test_key)
        if result and result.get("invalidated"):
            return None  # 已标记失效
        return result
    
    def save_test_result(self, test_key: str, result: Dict):
        """保存测试结果"""
        results = {}
        if self.results_file.exists():
            with open(self.results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        results[test_key] = {
            **result,
            "cached_at": datetime.now().isoformat()
        }
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def invalidate_test_result(self, test_key: str) -> bool:
        """手动标记测试结果失效"""
        if not self.results_file.exists():
            return False
        with open(self.results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        if test_key in results:
            results[test_key]["invalidated"] = True
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            return True
        return False
    
    def clear_test_results(self) -> bool:
        """清除所有测试结果缓存"""
        if self.results_file.exists():
            self.results_file.unlink()
            return True
        return False
    
    # ========== 失败记录缓存 (永久) ==========
    
    def record_failure(self, item_type: str, item_id: str, error: str):
        """记录失败项"""
        failures = {"templates": {}, "ports": {}}
        if self.failures_file.exists():
            with open(self.failures_file, 'r', encoding='utf-8') as f:
                failures = json.load(f)
        
        current_retry = failures.get(item_type, {}).get(item_id, {}).get("retry_count", 0)
        failures[item_type][item_id] = {
            "error": error,
            "failed_at": datetime.now().isoformat(),
            "retry_count": current_retry + 1
        }
        
        with open(self.failures_file, 'w', encoding='utf-8') as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)
    
    def get_failed_items(self, item_type: str) -> List[str]:
        """获取失败项列表"""
        if not self.failures_file.exists():
            return []
        with open(self.failures_file, 'r', encoding='utf-8') as f:
            failures = json.load(f)
        return list(failures.get(item_type, {}).keys())
    
    def clear_failure_record(self, item_type: str, item_id: str) -> bool:
        """清除特定失败记录"""
        if not self.failures_file.exists():
            return False
        with open(self.failures_file, 'r', encoding='utf-8') as f:
            failures = json.load(f)
        if item_id in failures.get(item_type, {}):
            del failures[item_type][item_id]
            with open(self.failures_file, 'w', encoding='utf-8') as f:
                json.dump(failures, f, indent=2)
            return True
        return False
    
    def clear_all_failures(self) -> bool:
        """清除所有失败记录"""
        if self.failures_file.exists():
            self.failures_file.unlink()
            return True
        return False
    
    # ========== 通用管理 ==========
    
    def clear_all_cache(self):
        """清除所有缓存"""
        self.clear_image_uuids()
        self.clear_test_results()
        self.clear_all_failures()
    
    def get_cache_summary(self) -> Dict:
        """获取缓存摘要"""
        summary = {
            "image_uuids": {},
            "test_results": {"total": 0, "valid": 0, "invalidated": 0},
            "failures": {"templates": 0, "ports": 0}
        }
        
        # 图片UUID
        if self.uuids_file.exists():
            with open(self.uuids_file, 'r', encoding='utf-8') as f:
                summary["image_uuids"] = json.load(f)
        
        # 测试结果
        if self.results_file.exists():
            with open(self.results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
                summary["test_results"]["total"] = len(results)
                summary["test_results"]["valid"] = sum(
                    1 for r in results.values() if not r.get("invalidated")
                )
                summary["test_results"]["invalidated"] = sum(
                    1 for r in results.values() if r.get("invalidated")
                )
        
        # 失败记录
        if self.failures_file.exists():
            with open(self.failures_file, 'r', encoding='utf-8') as f:
                failures = json.load(f)
                summary["failures"]["templates"] = len(failures.get("templates", {}))
                summary["failures"]["ports"] = len(failures.get("ports", {}))
        
        return summary


# 全局实例
_cache_manager: Optional[TestCacheManager] = None


def get_cache_manager() -> TestCacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = TestCacheManager()
    return _cache_manager


# 便捷函数
def get_test_image_uuid(image_type: str = "portrait") -> Optional[str]:
    """便捷获取测试图片UUID"""
    return get_cache_manager().get_image_uuid(image_type)


def cache_test_result(test_key: str, result: Dict):
    """便捷保存测试结果"""
    get_cache_manager().save_test_result(test_key, result)


def get_cached_test_result(test_key: str) -> Optional[Dict]:
    """便捷获取测试结果"""
    return get_cache_manager().get_test_result(test_key)
