#!/usr/bin/env python3
"""
统一配置管理
支持环境变量和.env文件
"""
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class Config:
    """统一配置管理"""
    
    # API 配置
    BASE_URL = "https://vivago.ai/api/gw"
    
    # 存储配置
    STORAGE_ENDPOINT = "http://storage.googleapis.com"
    STORAGE_BUCKET = "hidreamai-image"
    
    # 测试配置
    DEFAULT_MAX_RETRIES = 60
    DEFAULT_RETRY_DELAY = 3
    DEFAULT_TIMEOUT = 20
    MAX_POLL_ATTEMPTS = 30
    POLL_INTERVAL = 10
    
    @classmethod
    def get_token(cls) -> str:
        """获取API Token"""
        token = os.getenv("HIDREAM_TOKEN")
        if not token:
            raise ImportError(
                "HIDREAM_TOKEN environment variable not set.\n"
                "Please set it or create a .env file (see .env.example)"
            )
        return token
    
    @classmethod
    def get_storage_credentials(cls) -> tuple:
        """获取存储凭证"""
        ak = os.getenv("STORAGE_AK")
        sk = os.getenv("STORAGE_SK")
        if not ak or not sk:
            raise ImportError(
                "STORAGE_AK and STORAGE_SK environment variables must be set for image upload.\n"
                "Please set them or create a .env file (see .env.example)"
            )
        return ak, sk
    
    @classmethod
    def get_test_image_uuid(cls) -> Optional[str]:
        """获取测试用的图片UUID"""
        return os.getenv("TEST_IMAGE_UUID")
    
    @classmethod
    def get_test_config(cls) -> dict:
        """获取测试配置"""
        return {
            "max_attempts": int(os.getenv("TEST_MAX_ATTEMPTS", cls.MAX_POLL_ATTEMPTS)),
            "poll_interval": int(os.getenv("TEST_POLL_INTERVAL", cls.POLL_INTERVAL)),
        }
