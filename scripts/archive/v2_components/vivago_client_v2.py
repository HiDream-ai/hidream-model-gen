#!/usr/bin/env python3
"""
简化的VivagoClient - 使用组件化的设计
"""
import json
import os
from typing import Optional, Dict, Any, List
import requests
import boto3
from botocore.config import Config
import logging

from config import Config as AppConfig
from config_manager import ConfigManager, get_config_manager
from task_poller import TaskPoller
from image_uploader import ImageUploader
from type_defs import TaskStatus, JSONDict
from exceptions import (
    MissingCredentialError,
    InvalidPortError,
    TaskFailedError,
    TaskRejectedError,
    ImageUploadError
)

logger = logging.getLogger(__name__)


class VivagoClientV2:
    """
    Vivago API Client V2 - 组件化设计
    
    职责：
    - 作为facade组合各个组件
    - 提供简洁的API接口
    
    组件：
    - ConfigManager: 配置管理
    - TaskPoller: 任务轮询
    - ImageUploader: 图片上传
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        storage_ak: Optional[str] = None,
        storage_sk: Optional[str] = None,
        base_url: str = "https://vivago.ai/api/gw"
    ):
        """
        初始化客户端
        
        Args:
            token: API token（默认从环境变量读取）
            storage_ak: 存储access key（可选）
            storage_sk: 存储secret key（可选）
            base_url: API基础URL
        """
        # 获取token
        self.token = token or AppConfig.get_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "X-accept-language": "en",
        }
        self.base_url = base_url
        
        # 初始化配置管理器
        self.config_manager = get_config_manager()
        
        # 初始化任务轮询器
        self.poller = TaskPoller(self)
        
        # 初始化图片上传器（如果有凭证）
        self.uploader: Optional[ImageUploader] = None
        if storage_ak and storage_sk:
            s3_client = boto3.client(
                's3',
                endpoint_url=AppConfig.STORAGE_ENDPOINT,
                aws_access_key_id=storage_ak,
                aws_secret_access_key=storage_sk,
                config=Config(s3={'addressing_style': 'virtual'})
            )
            self.uploader = ImageUploader(s3_client)
    
    def upload_image(self, image_path: str) -> str:
        """上传图片"""
        if not self.uploader:
            ak, sk = AppConfig.get_storage_credentials()
            s3_client = boto3.client(
                's3',
                endpoint_url=AppConfig.STORAGE_ENDPOINT,
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                config=Config(s3={'addressing_style': 'virtual'})
            )
            self.uploader = ImageUploader(s3_client)
        
        return self.uploader.upload(image_path)
    
    def _get_port_config(self, port_id: str) -> Dict[str, Any]:
        """获取端口配置"""
        config = self.config_manager.get_port(port_id)
        if not config:
            available = self.config_manager.list_ports()
            raise InvalidPortError(port_id, available_ports=list(available.keys()))
        return config.to_dict()
    
    def _post(self, endpoint: str, payload: Dict) -> JSONDict:
        """POST请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    
    def get_result(self, task_id: str, endpoint: str) -> Optional[JSONDict]:
        """获取任务结果"""
        url = f"{self.base_url}{endpoint}"
        payload = {"task_id": task_id}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Get result error: {e}")
            return None
    
    # ========== 一级功能API ==========
    
    def text_to_image(
        self,
        prompt: str,
        port: str = "kling-image",
        wh_ratio: str = "1:1",
        batch_size: int = 1,
        **kwargs
    ) -> List[JSONDict]:
        """文生图"""
        config = self._get_port_config(port)
        
        payload = {
            "module": "image_gen_kling" if "kling" in port else "txt2img",
            "version": config['version'],
            "prompt": prompt,
            "en_prompt": "",
            "negative_prompt": "",
            "en_negative_prompt": "",
            "magic_prompt": kwargs.get('magic_prompt', ''),
            "style": kwargs.get('style', 'default'),
            "width": -1,
            "height": -1,
            "images": [],
            "masks": [],
            "params": {
                "wh_ratio": wh_ratio,
                "batch_size": batch_size,
                "mode": kwargs.get('mode', 'Fast'),
                "x": 0,
                "y": 0,
                "seed": kwargs.get('seed', -1)
            }
        }
        
        response = self._post(config['endpoint'], payload)
        
        if response.get('code') != 0:
            raise TaskFailedError("generation", response.get('msg', 'Unknown error'))
        
        task_id = response['result']['task_id']
        
        # 轮询结果
        result = self.poller.poll(task_id, config['result_endpoint'])
        
        if not result:
            raise TaskFailedError(task_id, "Timeout or failed")
        
        return result.get('result', [])
    
    def image_to_video(
        self,
        prompt: str,
        image_uuid: str,
        port: str = "v3Pro",
        wh_ratio: str = "1:1",
        duration: int = 5,
        **kwargs
    ) -> List[JSONDict]:
        """图生视频"""
        config = self._get_port_config(port)
        
        payload = {
            "module": config.get('algo_type', 'video_diffusion'),
            "version": config['version'],
            "prompt": prompt,
            "en_prompt": "",
            "negative_prompt": "",
            "en_negative_prompt": "",
            "magic_prompt": "",
            "images": [image_uuid],
            "masks": [],
            "videos": [],
            "audios": [],
            "params": {
                "wh_ratio": wh_ratio,
                "duration": duration,
                "mode": kwargs.get('mode', 'Fast'),
                "seed": kwargs.get('seed', -1),
                "motion": kwargs.get('motion', 0),
                "batch_size": 1
            }
        }
        
        response = self._post(config['endpoint'], payload)
        
        if response.get('code') != 0:
            raise TaskFailedError("generation", response.get('msg', 'Unknown error'))
        
        task_id = response['result']['task_id']
        result = self.poller.poll(task_id, config['result_endpoint'])
        
        if not result:
            raise TaskFailedError(task_id, "Timeout or failed")
        
        return result.get('result', [])
    
    def template_to_video(
        self,
        image_uuid: str,
        template: str,
        wh_ratio: str = "1:1",
        **kwargs
    ) -> JSONDict:
        """视频模板"""
        from template_manager import get_template_manager
        
        manager = get_template_manager()
        template_data = manager.get_template(template)
        
        if not template_data:
            raise InvalidPortError(template)
        
        # 构建payload
        params = template_data.get('params', {})
        inner_params = params.get('params', {})
        custom_params = inner_params.get('custom_params', {})
        
        payload = {
            "module": params.get('module', 'proto_transformer'),
            "version": params.get('version', 'v1'),
            "prompt": params.get('prompt', ''),
            "en_prompt": "",
            "negative_prompt": "",
            "en_negative_prompt": "",
            "magic_prompt": "",
            "template_id": params.get('template_id', ''),
            "images": [image_uuid],
            "masks": [],
            "videos": [],
            "audios": params.get('audios', []),
            "params": {
                "wh_ratio": wh_ratio,
                "mode": kwargs.get('mode', 'Fast'),
                "batch_size": 1,
                "custom_params": custom_params
            }
        }
        
        response = self._post(template_data['endpoint'], payload)
        
        if response.get('code') != 0:
            raise TaskFailedError("generation", response.get('msg', 'Unknown error'))
        
        task_id = response['result']['task_id']
        result = self.poller.poll(task_id, template_data['result_endpoint'])
        
        if not result:
            raise TaskFailedError(task_id, "Timeout or failed")
        
        return result


# 便捷函数
def create_client_v2(
    token: Optional[str] = None,
    storage_ak: Optional[str] = None,
    storage_sk: Optional[str] = None
) -> VivagoClientV2:
    """创建V2客户端"""
    return VivagoClientV2(token, storage_ak, storage_sk)
