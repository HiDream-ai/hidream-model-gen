#!/usr/bin/env python3
"""
测试资源管理器
管理测试图片和预上传UUID
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional

# 添加scripts到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from vivago_client import create_client
from fixtures.cache_manager import get_cache_manager


class TestAssetManager:
    """
    测试资源管理器
    
    负责:
    1. 管理测试图片文件
    2. 预上传图片并缓存UUID
    3. 提供统一的测试资源访问
    """
    
    FIXTURES_DIR = Path(__file__).parent
    IMAGES_DIR = FIXTURES_DIR / "images"
    
    # 测试图片配置
    TEST_IMAGES = {
        "portrait": {
            "filename": "portrait.jpg",
            "description": "人像照片，用于人物相关模板"
        },
        "landscape": {
            "filename": "landscape.jpg",
            "description": "风景照片，用于风景相关模板"
        },
        "product": {
            "filename": "product.jpg",
            "description": "产品照片，用于产品展示模板"
        },
        "animal": {
            "filename": "animal.jpg",
            "description": "动物照片，用于动物相关模板"
        }
    }
    
    def __init__(self):
        self.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.cache = get_cache_manager()
    
    def check_test_images(self) -> Dict[str, bool]:
        """检查测试图片是否存在"""
        status = {}
        for image_type, config in self.TEST_IMAGES.items():
            image_path = self.IMAGES_DIR / config["filename"]
            status[image_type] = image_path.exists()
        return status
    
    def get_image_path(self, image_type: str) -> Optional[Path]:
        """获取测试图片路径"""
        if image_type not in self.TEST_IMAGES:
            return None
        image_path = self.IMAGES_DIR / self.TEST_IMAGES[image_type]["filename"]
        if image_path.exists():
            return image_path
        return None
    
    def get_image_uuid(self, image_type: str = "portrait", auto_upload: bool = True) -> Optional[str]:
        """
        获取测试图片UUID
        
        Args:
            image_type: 图片类型 (portrait/landscape/product/animal)
            auto_upload: 如果未缓存，是否自动上传
            
        Returns:
            图片UUID或None
        """
        # 先检查缓存
        cached_uuid = self.cache.get_image_uuid(image_type)
        if cached_uuid:
            return cached_uuid
        
        # 如果允许自动上传
        if auto_upload:
            return self.upload_image(image_type)
        
        return None
    
    def upload_image(self, image_type: str = "portrait") -> Optional[str]:
        """
        上传测试图片并缓存UUID
        
        Args:
            image_type: 图片类型
            
        Returns:
            上传后的UUID或None
        """
        image_path = self.get_image_path(image_type)
        if not image_path:
            print(f"❌ 测试图片不存在: {image_type}")
            return None
        
        try:
            client = create_client()
            uuid = client.upload_image(str(image_path))
            
            # 缓存UUID
            self.cache.save_image_uuid(image_type, uuid)
            print(f"✅ 已上传 {image_type}: {uuid}")
            return uuid
            
        except Exception as e:
            print(f"❌ 上传失败 {image_type}: {e}")
            return None
    
    def upload_all_images(self) -> Dict[str, Optional[str]]:
        """上传所有测试图片"""
        results = {}
        for image_type in self.TEST_IMAGES.keys():
            print(f"📤 正在上传 {image_type}...")
            uuid = self.upload_image(image_type)
            results[image_type] = uuid
        return results
    
    def setup_all(self) -> bool:
        """
        初始化所有测试资源
        
        Returns:
            是否全部成功
        """
        print("🔧 初始化测试资源...")
        
        # 检查图片
        status = self.check_test_images()
        missing = [k for k, v in status.items() if not v]
        
        if missing:
            print(f"❌ 缺少测试图片: {missing}")
            print(f"   请在 {self.IMAGES_DIR} 目录放置以下图片:")
            for image_type in missing:
                print(f"   - {self.TEST_IMAGES[image_type]['filename']}: {self.TEST_IMAGES[image_type]['description']}")
            return False
        
        # 检查/上传UUID
        for image_type in self.TEST_IMAGES.keys():
            uuid = self.get_image_uuid(image_type, auto_upload=False)
            if uuid:
                print(f"✅ {image_type}: {uuid} (已缓存)")
            else:
                print(f"📤 {image_type}: 需要上传...")
                self.upload_image(image_type)
        
        print("✅ 测试资源初始化完成")
        return True
    
    def get_status(self) -> Dict:
        """获取测试资源状态"""
        return {
            "images": self.check_test_images(),
            "uuids": self.cache.list_cached_images()
        }


# 便捷函数
def get_test_asset_manager() -> TestAssetManager:
    return TestAssetManager()


def get_test_uuid(image_type: str = "portrait") -> Optional[str]:
    """便捷获取测试UUID"""
    return get_test_asset_manager().get_image_uuid(image_type)


if __name__ == "__main__":
    # 运行: python tests/fixtures/test_assets.py
    manager = get_test_asset_manager()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # 查看状态
        status = manager.get_status()
        print("\n📊 测试资源状态:")
        print(f"图片文件: {status['images']}")
        print(f"缓存UUID: {status['uuids']}")
    else:
        # 初始化
        manager.setup_all()
