#!/usr/bin/env python3
"""
Tier 1: 单元测试 (Mock-based，零API成本)
使用responses库Mock所有API调用
"""
import pytest
import responses
import json
import sys
import os
from unittest.mock import Mock, patch

# 添加scripts到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from vivago_client import VivagoClient
from vivago_client_v2 import VivagoClientV2
from template_manager import TemplateManager
from config_manager import ConfigManager
from exceptions import (
    TaskFailedError, TaskRejectedError,
    InvalidPortError, MissingCredentialError
)
from type_defs import TaskStatus


# ============== Fixtures ==============

@pytest.fixture
def mock_api():
    """Mock Vivago API响应"""
    with responses.RequestsMock() as rsps:
        # Mock 文生图
        rsps.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/image_gen_kling/async',
            json={'code': 0, 'result': {'task_id': 'mock-task-123'}},
            status=200
        )
        rsps.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/txt2img/async/results',
            json={'code': 0, 'result': {'sub_task_results': [
                {'task_status': 1, 'result': ['http://mock.com/image.jpg']}
            ]}},
            status=200
        )
        
        # Mock 图生视频
        rsps.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/video/video_diffusion/async',
            json={'code': 0, 'result': {'task_id': 'mock-task-456'}},
            status=200
        )
        rsps.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/video/video_diffusion/async/results',
            json={'code': 0, 'result': {'sub_task_results': [
                {'task_status': 1, 'result': ['http://mock.com/video.mp4']}
            ]}},
            status=200
        )
        
        yield rsps


@pytest.fixture
def client():
    """创建测试客户端"""
    return VivagoClient(token="mock-token")


@pytest.fixture
def client_v2():
    """创建V2测试客户端"""
    return VivagoClientV2(token="mock-token")


# ============== VivagoClient 测试 ==============

class TestVivagoClient:
    """测试 VivagoClient 基础功能"""
    
    def test_initialization(self):
        """测试客户端初始化"""
        client = VivagoClient(token="test-token")
        assert client.token == "test-token"
        assert client.headers["Authorization"] == "Bearer test-token"
    
    def test_load_ports_config(self, client):
        """测试端口配置加载"""
        config = client._load_ports_config()
        assert "base_url" in config
        assert "categories" in config
    
    @responses.activate
    def test_text_to_image_mock(self, client):
        """测试文生图 - Mock"""
        # Mock API响应
        responses.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/image_gen_kling/async',
            json={'code': 0, 'result': {'task_id': 'mock-123'}},
            status=200
        )
        responses.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/txt2img/async/results',
            json={'code': 0, 'result': {'sub_task_results': [
                {'task_status': 1, 'result': ['http://test.jpg']}
            ]}},
            status=200
        )
        
        result = client.text_to_image(prompt="test", port="kling-image")
        assert result is not None
        assert len(result) > 0
    
    def test_get_port_config_valid(self, client):
        """测试获取有效端口配置"""
        config, port_name = client._get_port_config('text_to_image', 'kling-image')
        assert port_name == 'kling-image'
        assert 'endpoint' in config
    
    def test_get_port_config_invalid(self, client):
        """测试获取无效端口配置"""
        with pytest.raises(ValueError) as exc_info:
            client._get_port_config('text_to_image', 'invalid-port')
        assert 'invalid-port' in str(exc_info.value)


# ============== VivagoClientV2 测试 ==============

class TestVivagoClientV2:
    """测试 VivagoClientV2"""
    
    def test_v2_initialization(self):
        """测试V2客户端初始化"""
        with patch('vivago_client_v2.get_config_manager'):
            client = VivagoClientV2(token="test-token")
            assert client.token == "test-token"
    
    @responses.activate
    def test_v2_text_to_image(self):
        """测试V2文生图"""
        responses.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/image_gen_kling/async',
            json={'code': 0, 'result': {'task_id': 'mock-123'}},
            status=200
        )
        responses.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/txt2img/async/results',
            json={'code': 0, 'result': {'sub_task_results': [
                {'task_status': 1, 'result': ['http://test.jpg']}
            ]}},
            status=200
        )
        
        with patch('vivago_client_v2.get_config_manager'):
            client = VivagoClientV2(token="test-token")
            # Mock poller to return immediately
            client.poller.poll = Mock(return_value={
                'task_status': 1,
                'result': ['http://test.jpg']
            })
            
            result = client.text_to_image(prompt="test")
            assert result is not None


# ============== TemplateManager 测试 ==============

class TestTemplateManager:
    """测试 TemplateManager"""
    
    def test_load_templates(self):
        """测试模板加载"""
        manager = TemplateManager()
        templates = manager.list_templates()
        assert len(templates) > 0
    
    def test_get_template_existing(self):
        """测试获取存在的模板"""
        manager = TemplateManager()
        templates = manager.list_templates()
        if templates:
            first_id = list(templates.keys())[0]
            template = manager.get_template(first_id)
            assert template is not None
            assert 'name' in template
    
    def test_get_template_nonexistent(self):
        """测试获取不存在的模板"""
        manager = TemplateManager()
        template = manager.get_template('nonexistent_template_xyz')
        assert template is None
    
    def test_template_id_generation(self):
        """测试模板ID生成"""
        manager = TemplateManager()
        # 测试ID生成逻辑
        test_cases = [
            ("Hello World", "hello_world"),
            ("Test-Template", "test_template"),
            ("It's OK", "its_ok"),
        ]
        for input_name, expected_id in test_cases:
            generated = manager._generate_template_id(input_name)
            assert generated == expected_id


# ============== ConfigManager 测试 ==============

class TestConfigManager:
    """测试 ConfigManager"""
    
    def test_load_config(self):
        """测试配置加载"""
        manager = ConfigManager()
        ports = manager.list_ports()
        assert len(ports) > 0
    
    def test_get_port(self):
        """测试获取端口配置"""
        manager = ConfigManager()
        # 测试标准端口
        port = manager.get_port("kling-image")
        assert port is not None
        assert port.port_id == "kling-image"
    
    def test_get_ports_by_category(self):
        """测试按类别获取端口"""
        manager = ConfigManager()
        image_ports = manager.get_ports_by_category("text_to_image")
        assert len(image_ports) >= 3  # kling, hidream, nano-banana


# ============== 异常体系测试 ==============

class TestExceptions:
    """测试自定义异常"""
    
    def test_task_failed_error(self):
        """测试任务失败异常"""
        error = TaskFailedError('task_123', 'Out of credits')
        assert error.task_id == 'task_123'
        assert error.reason == 'Out of credits'
        assert 'task_123' in str(error)
    
    def test_task_rejected_error(self):
        """测试任务被拒绝异常"""
        error = TaskRejectedError('task_456')
        assert error.task_id == 'task_456'
        assert 'Content policy violation' in str(error)
    
    def test_invalid_port_error_with_available(self):
        """测试无效端口异常（带可用端口列表）"""
        error = InvalidPortError(
            'bad_port',
            category='text_to_image',
            available_ports=['port1', 'port2']
        )
        assert error.port == 'bad_port'
        assert 'port1' in str(error)
        assert 'port2' in str(error)


# ============== 类型系统测试 ==============

class TestTypes:
    """测试类型定义"""
    
    def test_task_status_enum(self):
        """测试任务状态枚举"""
        assert TaskStatus.PENDING.value == 0
        assert TaskStatus.COMPLETED.value == 1
        assert TaskStatus.PROCESSING.value == 2
        assert TaskStatus.FAILED.value == 3
        assert TaskStatus.REJECTED.value == 4
    
    def test_task_status_from_int(self):
        """测试从整数获取状态"""
        assert TaskStatus(1) == TaskStatus.COMPLETED
        assert TaskStatus(3) == TaskStatus.FAILED


# ============== 缓存管理器测试 ==============

class TestCacheManager:
    """测试缓存管理器"""
    
    def test_cache_manager_singleton(self):
        """测试缓存管理器单例"""
        from fixtures.cache_manager import get_cache_manager
        cm1 = get_cache_manager()
        cm2 = get_cache_manager()
        assert cm1 is cm2
    
    def test_image_uuid_cache(self, tmp_path):
        """测试图片UUID缓存"""
        from fixtures.cache_manager import TestCacheManager
        
        cm = TestCacheManager()
        cm.uuids_file = tmp_path / "test_uuids.json"
        
        # 保存
        cm.save_image_uuid("portrait", "j_test_123")
        
        # 读取
        uuid = cm.get_image_uuid("portrait")
        assert uuid == "j_test_123"
    
    def test_test_result_cache_and_invalidate(self, tmp_path):
        """测试结果缓存和失效"""
        from fixtures.cache_manager import TestCacheManager
        
        cm = TestCacheManager()
        cm.results_file = tmp_path / "test_results.json"
        
        # 保存结果
        cm.save_test_result("test_key", {"status": "pass"})
        
        # 读取结果
        result = cm.get_test_result("test_key")
        assert result["status"] == "pass"
        
        # 标记失效
        cm.invalidate_test_result("test_key")
        
        # 再次读取应返回None
        result = cm.get_test_result("test_key")
        assert result is None


# ============== 运行入口 ==============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
