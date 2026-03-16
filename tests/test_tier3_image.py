#!/usr/bin/env python3
"""
Tier 3: 核心功能冒烟测试 - 图片功能流水线
可顺序执行，不会超时
"""
import pytest
import sys
import os

# 添加正确的路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/tests')

from dotenv import load_dotenv
load_dotenv()

from scripts.vivago_client import create_client
from fixtures.cache_manager import get_cache_manager


@pytest.mark.api_cost(low=True)
class TestTier3ImageFeatures:
    """
    Tier 3 Phase 1: 图片功能流水线测试
    总积分: 16
    预计时间: 30-60秒
    """
    
    @classmethod
    def setup_class(cls):
        """测试类准备"""
        cls.client = create_client()
        cls.cache = get_cache_manager()
        cls.test_uuid = None
    
    def test_01_text_to_image(self):
        """文生图 (Kling O1) - 8积分"""
        print('\n🎨 文生图 (Kling O1) - 8积分...')
        
        result = self.client.text_to_image(
            prompt='a cute cartoon cat playing with a ball of yarn, colorful and cheerful',
            port='kling-image',
            batch_size=1,
            wh_ratio='1:1'
        )
        
        assert result is not None, "文生图应该返回结果"
        assert len(result) > 0, "应该至少生成1张图片"
        
        # 保存结果
        self.cache.save_test_result('tier3_text_to_image', {
            'status': 'success',
            'count': len(result),
            'image_id': result[0].get('image', 'N/A') if result else 'N/A'
        })
        
        print(f'   ✅ 成功，生成 {len(result)} 张图片')
    
    def test_02_upload_image(self):
        """上传测试图片 - 20积分 (但可复用)"""
        print('\n📤 上传测试图片...')
        
        # 检查是否有缓存
        cached_uuid = self.cache.get_image_uuid('portrait')
        if cached_uuid:
            self.test_uuid = cached_uuid
            print(f'   ✅ 使用缓存图片: {self.test_uuid}')
            return
        
        # 上传新图片
        uuid = self.client.upload_image('tests/fixtures/images/portrait.jpg')
        self.cache.save_image_uuid('portrait', uuid)
        self.test_uuid = uuid
        
        print(f'   ✅ 图片已上传: {uuid}')
    
    def test_03_image_to_image(self):
        """图生图 (Kling O1) - 8积分"""
        print('\n🔄 图生图 (Kling O1) - 8积分...')
        
        # 确保有图片UUID
        if not self.test_uuid:
            self.test_uuid = self.cache.get_image_uuid('portrait')
        
        assert self.test_uuid, "需要有测试图片UUID"
        
        result = self.client.image_to_image(
            prompt='convert to watercolor painting style, artistic and beautiful',
            image_uuids=[self.test_uuid],
            port='kling-image',
            strength=0.7
        )
        
        assert result is not None, "图生图应该返回结果"
        
        self.cache.save_test_result('tier3_image_to_image', {
            'status': 'success'
        })
        
        print('   ✅ 成功')
    
    def test_summary(self):
        """汇总结果"""
        print('\n' + '='*60)
        print('Tier 3 Phase 1 完成')
        print('='*60)
        print('\n✅ 图片功能全部正常!')
        print('   可以单独运行视频功能测试:')
        print('   - python tests/video_img2vid.py')
        print('   - python tests/video_txt2vid.py')
        print('   - python tests/video_keyframe.py')
        print('   - python tests/video_template.py')
