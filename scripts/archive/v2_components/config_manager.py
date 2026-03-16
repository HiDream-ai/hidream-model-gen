#!/usr/bin/env python3
"""
统一配置管理器
解决 api_ports.json 和 templates_data.json 双配置源问题
提供单一配置源
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class PortConfig:
    """端口配置"""
    port_id: str
    display_name: str
    endpoint: str
    result_endpoint: str
    version: str
    algo_type: Optional[str] = None
    category: str = ""
    speed: str = "unknown"
    quality: str = "unknown"
    tested: bool = False
    notes: str = ""
    supported_ratios: List[str] = field(default_factory=lambda: ["1:1", "16:9", "9:16", "4:3", "3:4"])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "display_name": self.display_name,
            "endpoint": self.endpoint,
            "result_endpoint": self.result_endpoint,
            "version": self.version,
            "algo_type": self.algo_type,
            "speed": self.speed,
            "quality": self.quality,
            "tested": self.tested,
            "notes": self.notes,
            "supported_ratios": self.supported_ratios
        }


@dataclass
class TemplatePortConfig(PortConfig):
    """模板端口配置（继承自PortConfig）"""
    template_id: str = ""
    template_uuid: str = ""
    master_template_id: str = ""  # 原始模板ID
    result_type: Optional[str] = None  # "video" or "image"


class ConfigManager:
    """
    统一配置管理器
    
    单一职责：
    1. 从 templates_data.json 加载所有配置
    2. 提供配置查询接口
    3. 支持配置验证
    4. 管理测试状态
    
    消除 api_ports.json 的重复，templates_data.json 作为唯一数据源
    """
    
    def __init__(self, templates_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            templates_file: 模板数据文件路径，默认使用内置路径
        """
        if templates_file is None:
            base_dir = Path(__file__).parent
            templates_file = base_dir / 'templates_data.json'
        
        self.templates_file = Path(templates_file)
        self._templates: Dict[str, TemplatePortConfig] = {}
        self._categories: Dict[str, Dict[str, Any]] = {}
        
        self._load_config()
    
    def _load_config(self):
        """从 templates_data.json 加载配置"""
        if not self.templates_file.exists():
            raise FileNotFoundError(f"Templates file not found: {self.templates_file}")
        
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析每个模板
        for item in data:
            master = item.get('master_template', {})
            gen_params = item.get('gen_params', {})
            params = gen_params.get('params', {})
            inner_params = params.get('params', {})
            
            # 生成模板ID
            template_id = self._generate_template_id(master.get('name', ''))
            
            # 获取支持的宽高比
            supported_ratios = self._get_supported_ratios(gen_params.get('inputs', []))
            
            # 创建配置
            config = TemplatePortConfig(
                port_id=template_id,
                display_name=master.get('name', template_id),
                endpoint=gen_params.get('generate_path', '').replace('/api/gw', ''),
                result_endpoint=self._get_result_endpoint(gen_params),
                version=params.get('version', 'v1'),
                algo_type=gen_params.get('algo_type'),
                category='template_to_video',
                template_id=params.get('template_id', ''),
                template_uuid=master.get('uuid', ''),
                master_template_id=inner_params.get('custom_params', {}).get('master_template_id', ''),
                supported_ratios=supported_ratios
            )
            
            self._templates[template_id] = config
        
        # 初始化标准端口配置（非模板端口）
        self._init_standard_ports()
        
        print(f"ConfigManager: Loaded {len(self._templates)} template ports")
    
    def _init_standard_ports(self):
        """初始化标准API端口（非模板）"""
        # 文生图端口
        standard_ports = [
            PortConfig(
                port_id="kling-image",
                display_name="Kling O1",
                endpoint="/v3/image/image_gen_kling/async",
                result_endpoint="/v3/image/txt2img/async/results",
                version="kling-image-o1",
                category="text_to_image",
                speed="fast",
                quality="excellent",
                tested=True
            ),
            PortConfig(
                port_id="hidream-txt2img",
                display_name="Vivago.ai 2.0",
                endpoint="/v3/image/txt2img/async",
                result_endpoint="/v3/image/txt2img/async/results",
                version="hidream",
                category="text_to_image",
                speed="medium",
                quality="good",
                tested=True
            ),
            PortConfig(
                port_id="nano-banana",
                display_name="Nano Banana 2",
                endpoint="/v3/image/image_gen_std/async",
                result_endpoint="/v3/image/image/async/results/batch",
                version="nano-banana",
                category="text_to_image",
                speed="slow",
                quality="superior",
                tested=True
            ),
            # 图生视频端口
            PortConfig(
                port_id="v3Pro",
                display_name="Vivago.ai 2.0",
                endpoint="/v3/video/video_diffusion_img2vid/async",
                result_endpoint="/v3/video/video_diffusion/async/results",
                version="v3Pro",
                category="image_to_video",
                speed="slow",
                quality="superior",
                tested=True
            ),
            PortConfig(
                port_id="v3L",
                display_name="Vivago.ai 2.0 360p",
                endpoint="/v3/video/video_diffusion_img2vid/async",
                result_endpoint="/v3/video/video_diffusion/async/results",
                version="v3L",
                category="image_to_video",
                speed="fast",
                quality="good",
                tested=True
            ),
            PortConfig(
                port_id="kling-video",
                display_name="Kling video O1",
                endpoint="/v3/video/video_diffusion/async",
                result_endpoint="/v3/video/video_diffusion/async/results",
                version="kling-video",
                algo_type="video_diffusion",
                category="image_to_video",
                speed="medium",
                quality="superior",
                tested=True
            ),
        ]
        
        for port in standard_ports:
            self._templates[port.port_id] = port
    
    def _generate_template_id(self, name: str) -> str:
        """从模板名称生成ID"""
        import re
        # 使用更安全的slug生成
        slug = (name.lower()
                .replace(' ', '_')
                .replace("'", "")
                .replace('-', '_')
                .replace('（', '')
                .replace('）', '')
                .replace('(', '')
                .replace(')', ''))
        # 移除非字母数字下划线字符
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        return slug or "unnamed_template"
    
    def _get_supported_ratios(self, inputs: List[Dict]) -> List[str]:
        """从inputs获取支持的宽高比"""
        for inp in inputs:
            if inp.get('key') == 'wh_ratio' and 'value_list' in inp:
                return inp['value_list']
        return ["1:1", "16:9", "9:16", "4:3", "3:4"]
    
    def _get_result_endpoint(self, gen_params: Dict) -> str:
        """确定回调路径"""
        algo_type = gen_params.get('algo_type', '')
        result_path = gen_params.get('result_path', '')
        
        # proto_transformer 和 avatar_transformer 使用 video_diffusion 回调
        if algo_type in ['proto_transformer', 'avatar_transformer']:
            return '/v3/video/video_diffusion/async/results'
        
        return result_path.replace('/api/gw', '') if result_path else '/v3/video/video_diffusion/async/results'
    
    def get_port(self, port_id: str) -> Optional[PortConfig]:
        """获取端口配置"""
        return self._templates.get(port_id)
    
    def get_ports_by_category(self, category: str) -> Dict[str, PortConfig]:
        """按类别获取端口"""
        return {
            k: v for k, v in self._templates.items()
            if v.category == category
        }
    
    def list_ports(self) -> Dict[str, str]:
        """列出所有端口ID和显示名称"""
        return {k: v.display_name for k, v in self._templates.items()}
    
    def list_categories(self) -> List[str]:
        """列出所有类别"""
        categories = set()
        for config in self._templates.values():
            categories.add(config.category)
        return sorted(categories)
    
    def update_test_status(self, port_id: str, tested: bool, 
                          result_type: Optional[str] = None,
                          notes: str = ""):
        """更新端口测试状态"""
        if port_id in self._templates:
            config = self._templates[port_id]
            config.tested = tested
            if notes:
                config.notes = notes
            if isinstance(config, TemplatePortConfig) and result_type:
                config.result_type = result_type
    
    def get_tested_ports(self) -> Dict[str, PortConfig]:
        """获取已测试的端口"""
        return {k: v for k, v in self._templates.items() if v.tested}
    
    def get_untested_ports(self) -> Dict[str, PortConfig]:
        """获取未测试的端口"""
        return {k: v for k, v in self._templates.items() if not v.tested}


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例（单例模式）"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reset_config_manager():
    """重置配置管理器（主要用于测试）"""
    global _config_manager
    _config_manager = None
