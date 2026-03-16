#!/usr/bin/env python3
"""
Tier 4: 图片端口采样测试 - 流水线
图片相关端口可顺序测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))

from dotenv import load_dotenv
load_dotenv()

from vivago_client import create_client
from config_manager import get_config_manager
from fixtures.cache_manager import get_cache_manager


# 图片端口配置 (低积分，可流水线测试)
IMAGE_PORT_SAMPLES = {
    "kling-image": {
        "type": "text_to_image",
        "credits": 8,
        "test": "text_to_image"
    },
    "hidream-txt2img": {
        "type": "text_to_image",
        "credits": 2,
        "test": "text_to_image"
    },
    "nano-banana": {
        "type": "text_to_image",
        "credits": 10,
        "test": "text_to_image"
    },
}


@pytest.mark.api_cost(medium=True)
class TestTier4ImagePorts:
    """
    Tier 4 Phase 1: 图片端口采样测试
    总积分: ~20
    预计时间: 1-2分钟
    """
    
    @classmethod
    def setup_class(cls):
        cls.client = create_client()
        cls.cache = get_cache_manager()
        cls.config = get_config_manager()
        cls.test_uuid = None
    
    def get_test_image(self):
        """获取测试图片"""
        if not self.test_uuid:
            self.test_uuid = self.cache.get_image_uuid('portrait')
        return self.test_uuid
    
    def test_port_kling_image(self):
        """测试 Kling O1 - 8积分"""
        print('\n🔌 测试端口: kling-image (Kling O1) - 8积分...')
        
        result = self.client.text_to_image(
            prompt='a cute puppy playing in garden',
            port='kling-image',
            batch_size=1
        )
        
        assert result is not None
        self.cache.save_test_result('port_kling_image', {'status': 'success'})
        print('   ✅ 通过')
    
    def test_port_hidream(self):
        """测试 Vivago.ai 2.0 - 2积分"""
        print('\n🔌 测试端口: hidream-txt2img (Vivago 2.0) - 2积分...')
        
        result = self.client.text_to_image(
            prompt='sunset over mountains',
            port='hidream-txt2img',
            batch_size=1
        )
        
        assert result is not None
        self.cache.save_test_result('port_hidream', {'status': 'success'})
        print('   ✅ 通过')
    
    def test_port_nano_banana(self):
        """测试 Nano Banana 2 - 10积分"""
        print('\n🔌 测试端口: nano-banana (Nano Banana 2) - 10积分...')
        
        result = self.client.text_to_image(
            prompt='fresh fruit arrangement',
            port='nano-banana',
            batch_size=1
        )
        
        assert result is not None
        self.cache.save_test_result('port_nano_banana', {'status': 'success'})
        print('   ✅ 通过')
    
    def test_port_kling_img2img(self):
        """测试 Kling O1 图生图 - 8积分"""
        print('\n🔌 测试端口: kling-image 图生图 - 8积分...')
        
        test_uuid = self.get_test_image()
        assert test_uuid, "需要测试图片"
        
        result = self.client.image_to_image(
            prompt='convert to oil painting style',
            image_uuids=[test_uuid],
            port='kling-image',
            strength=0.7
        )
        
        assert result is not None
        self.cache.save_test_result('port_kling_img2img', {'status': 'success'})
        print('   ✅ 通过')
    
    def test_summary(self):
        """汇总"""
        print('\n' + '='*60)
        print('Tier 4 图片端口测试完成')
        print('='*60)
        print('\n✅ 图片端口全部正常!')
        print('   视频端口测试请单独运行:')
        print('   - python tests/tier4_video_v3l.py')
        print('   - python tests/tier4_video_kling.py')
