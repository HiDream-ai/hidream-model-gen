#!/usr/bin/env python3
"""
类型提示支持模块
为整个项目提供类型定义
"""
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态码"""
    PENDING = 0
    COMPLETED = 1
    PROCESSING = 2
    FAILED = 3
    REJECTED = 4


class AspectRatio(Enum):
    """支持的宽高比"""
    RATIO_1_1 = "1:1"
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_4_3 = "4:3"
    RATIO_3_4 = "3:4"


# 常用类型别名
JSONDict = Dict[str, Any]
TaskResult = Dict[str, Any]
PortConfig = Dict[str, Any]
TemplateConfig = Dict[str, Any]


@dataclass
class GenerationResult:
    """生成结果数据类"""
    task_id: str
    status: TaskStatus
    result_urls: List[str]
    result_type: str  # "image" or "video"
    duration: float
    
    def to_dict(self) -> JSONDict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result_urls": self.result_urls,
            "result_type": self.result_type,
            "duration": self.duration
        }


@dataclass  
class PortInfo:
    """端口信息数据类"""
    port_id: str
    display_name: str
    endpoint: str
    result_endpoint: str
    version: str
    speed: str
    quality: str
    tested: bool = False
    
    def to_dict(self) -> JSONDict:
        return {
            "port_id": self.port_id,
            "display_name": self.display_name,
            "endpoint": self.endpoint,
            "result_endpoint": self.result_endpoint,
            "version": self.version,
            "speed": self.speed,
            "quality": self.quality,
            "tested": self.tested
        }
