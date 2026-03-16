#!/usr/bin/env python3
"""
基础单元测试 - 使用 Mock 避免调用真实 API
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vivago_client import VivagoClient
from template_manager import TemplateManager
from exceptions import (
    TaskFailedError, TaskRejectedError, 
    InvalidPortError, MissingCredentialError
)


class TestVivagoClient:
    """测试 VivagoClient 核心功能"""
    
    @patch.dict(os.environ, {'HIDREAM_TOKEN': 'test_token'})
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = VivagoClient(token='test_token')
        assert client.token == 'test_token'
        assert client.headers['Authorization'] == 'Bearer test_token'
    
    def test_missing_token_raises_error(self):
        """测试缺少 token 时抛出错误"""
        with pytest.raises(MissingCredentialError):
            # 模拟环境变量不存在
            with patch.dict(os.environ, {}, clear=True):
                from config import Config
                Config.get_token()
    
    def test_invalid_port_raises_error(self):
        """测试无效端口抛出错误"""
        client = VivagoClient(token='test_token')
        
        with pytest.raises(ValueError) as exc_info:
            client._get_port_config('text_to_image', 'invalid_port')
        
        assert 'invalid_port' in str(exc_info.value)


class TestTemplateManager:
    """测试 TemplateManager"""
    
    def test_load_templates(self):
        """测试加载模板"""
        manager = TemplateManager()
        templates = manager.list_templates()
        
        # 应该加载了一些模板
        assert len(templates) > 0
        
        # 检查特定模板是否存在
        assert 'ghibli' in templates or 'renovation_old_photos' in templates
    
    def test_get_template(self):
        """测试获取单个模板"""
        manager = TemplateManager()
        
        # 获取存在的模板
        templates = manager.list_templates()
        if templates:
            first_id = list(templates.keys())[0]
            template = manager.get_template(first_id)
            
            assert template is not None
            assert 'name' in template
            assert 'uuid' in template
    
    def test_get_nonexistent_template(self):
        """测试获取不存在的模板"""
        manager = TemplateManager()
        template = manager.get_template('nonexistent_template_12345')
        
        assert template is None


class TestExceptions:
    """测试异常体系"""
    
    def test_task_failed_error(self):
        """测试任务失败异常"""
        error = TaskFailedError('task_123', 'Out of credits')
        
        assert error.task_id == 'task_123'
        assert error.reason == 'Out of credits'
        assert 'task_123' in str(error)
        assert 'Out of credits' in str(error)
    
    def test_task_rejected_error(self):
        """测试任务被拒绝异常"""
        error = TaskRejectedError('task_456')
        
        assert error.task_id == 'task_456'
        assert 'Content policy violation' in str(error)
    
    def test_invalid_port_error(self):
        """测试无效端口异常"""
        error = InvalidPortError(
            'bad_port', 
            category='text_to_image',
            available_ports=['port1', 'port2']
        )
        
        assert error.port == 'bad_port'
        assert error.category == 'text_to_image'
        assert 'port1' in str(error)
        assert 'port2' in str(error)


class TestConfig:
    """测试配置管理"""
    
    def test_config_has_required_constants(self):
        """测试配置包含必要常量"""
        from config import Config
        
        assert hasattr(Config, 'BASE_URL')
        assert hasattr(Config, 'DEFAULT_MAX_RETRIES')
        assert hasattr(Config, 'DEFAULT_RETRY_DELAY')
        assert hasattr(Config, 'STORAGE_ENDPOINT')
    
    @patch.dict(os.environ, {'HIDREAM_TOKEN': 'test_token_123'})
    def test_get_token_from_env(self):
        """测试从环境变量获取 token"""
        from config import Config
        
        token = Config.get_token()
        assert token == 'test_token_123'
    
    @patch.dict(os.environ, {'TEST_MAX_ATTEMPTS': '30', 'TEST_POLL_INTERVAL': '5'})
    def test_get_test_config(self):
        """测试获取测试配置"""
        from config import Config
        
        config = Config.get_test_config()
        assert config['max_attempts'] == 30
        assert config['poll_interval'] == 5


class TestFramework:
    """测试测试框架"""
    
    def test_template_test_result(self):
        """测试测试结果类"""
        from tests.framework import TemplateTestResult
        
        result = TemplateTestResult(
            template_id='test_template',
            success=True,
            result_type='video',
            duration=10.5,
            task_id='task_123'
        )
        
        assert result.template_id == 'test_template'
        assert result.success is True
        assert result.result_type == 'video'
        assert result.duration == 10.5
        
        # 测试序列化
        data = result.to_dict()
        assert data['template_id'] == 'test_template'
        assert data['success'] is True
        assert 'timestamp' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
