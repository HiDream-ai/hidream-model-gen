#!/usr/bin/env python3
"""
统一测试框架
消除测试脚本中的重复代码
"""
import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

# 添加 scripts 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vivago_client import create_client
from template_manager import get_template_manager
from config import Config
from exceptions import (
    VivagoError, TaskFailedError, TaskRejectedError, 
    TaskTimeoutError, TemplateNotFoundError
)


class TemplateTestResult:
    """单个模板测试结果"""
    
    def __init__(self, template_id: str, success: bool, 
                 result_type: Optional[str] = None,
                 error: Optional[str] = None,
                 duration: float = 0.0,
                 task_id: Optional[str] = None):
        self.template_id = template_id
        self.success = success
        self.result_type = result_type
        self.error = error
        self.duration = duration
        self.task_id = task_id
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "success": self.success,
            "result_type": self.result_type,
            "error": self.error,
            "duration": self.duration,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }


class TemplateTestRunner:
    """模板测试运行器"""
    
    def __init__(self, image_uuid: Optional[str] = None, 
                 max_attempts: int = None,
                 poll_interval: int = None):
        """
        初始化测试运行器
        
        Args:
            image_uuid: 测试用的图片UUID（默认从环境变量读取）
            max_attempts: 最大轮询次数
            poll_interval: 轮询间隔秒数
        """
        self.client = create_client()
        self.template_manager = get_template_manager()
        self.image_uuid = image_uuid or Config.get_test_image_uuid()
        
        test_config = Config.get_test_config()
        self.max_attempts = max_attempts or test_config["max_attempts"]
        self.poll_interval = poll_interval or test_config["poll_interval"]
        
        self.results: List[TemplateTestResult] = []
        
    def test_template(self, template_id: str, 
                      on_progress: Optional[Callable[[str, int], None]] = None) -> TemplateTestResult:
        """
        测试单个模板
        
        Args:
            template_id: 模板ID
            on_progress: 进度回调函数(template_id, attempt)
            
        Returns:
            TemplateTestResult 测试结果
        """
        start_time = time.time()
        
        # 检查模板是否存在
        template = self.template_manager.get_template(template_id)
        if not template:
            result = TemplateTestResult(
                template_id=template_id,
                success=False,
                error=f"Template {template_id} not found"
            )
            self.results.append(result)
            return result
        
        # 检查是否有测试图片
        if not self.image_uuid:
            result = TemplateTestResult(
                template_id=template_id,
                success=False,
                error="No test image UUID provided"
            )
            self.results.append(result)
            return result
        
        try:
            # 调用模板生成
            response = self.client.template_to_video(
                image_uuid=self.image_uuid,
                template=template_id,
                wh_ratio="1:1"
            )
            
            if not response:
                result = TemplateTestResult(
                    template_id=template_id,
                    success=False,
                    error="No response from API",
                    duration=time.time() - start_time
                )
                self.results.append(result)
                return result
            
            task_id = response.get('task_id')
            
            # 轮询等待结果
            for attempt in range(self.max_attempts):
                if on_progress:
                    on_progress(template_id, attempt + 1)
                
                time.sleep(self.poll_interval)
                
                status_response = self.client.get_result(task_id, 
                    endpoint=template.get('result_endpoint', '/v3/video/video_diffusion/async/results'))
                
                if not status_response:
                    continue
                
                code = status_response.get('code', -1)
                if code != 0:
                    continue
                
                result_data = status_response.get('result', {})
                sub_results = result_data.get('sub_task_results', [])
                
                if not sub_results:
                    continue
                
                task_info = sub_results[0]
                status = task_info.get('task_status', 0)
                
                if status == 1:  # 完成
                    result_urls = task_info.get('result', [])
                    result_type = "video" if any('.mp4' in str(url) for url in result_urls) else "image"
                    
                    result = TemplateTestResult(
                        template_id=template_id,
                        success=True,
                        result_type=result_type,
                        duration=time.time() - start_time,
                        task_id=task_id
                    )
                    self.results.append(result)
                    return result
                    
                elif status == 3:  # 失败
                    result = TemplateTestResult(
                        template_id=template_id,
                        success=False,
                        error="Task failed",
                        duration=time.time() - start_time,
                        task_id=task_id
                    )
                    self.results.append(result)
                    return result
                    
                elif status == 4:  # 被拒绝
                    result = TemplateTestResult(
                        template_id=template_id,
                        success=False,
                        error="Content rejected",
                        duration=time.time() - start_time,
                        task_id=task_id
                    )
                    self.results.append(result)
                    return result
            
            # 超时
            result = TemplateTestResult(
                template_id=template_id,
                success=False,
                error=f"Timeout after {self.max_attempts * self.poll_interval}s",
                duration=time.time() - start_time,
                task_id=task_id
            )
            self.results.append(result)
            return result
            
        except Exception as e:
            result = TemplateTestResult(
                template_id=template_id,
                success=False,
                error=str(e),
                duration=time.time() - start_time
            )
            self.results.append(result)
            return result
    
    def test_batch(self, template_ids: List[str],
                   on_template_start: Optional[Callable[[str, int, int], None]] = None,
                   on_template_complete: Optional[Callable[[TemplateTestResult], None]] = None) -> List[TemplateTestResult]:
        """
        批量测试模板
        
        Args:
            template_ids: 模板ID列表
            on_template_start: 开始回调(template_id, current, total)
            on_template_complete: 完成回调(result)
            
        Returns:
            List[TemplateTestResult] 所有结果
        """
        self.results = []
        total = len(template_ids)
        
        for i, template_id in enumerate(template_ids, 1):
            if on_template_start:
                on_template_start(template_id, i, total)
            
            result = self.test_template(template_id)
            
            if on_template_complete:
                on_template_complete(result)
        
        return self.results
    
    def generate_report(self) -> dict:
        """生成测试报告"""
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        failed = total - success
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "success": success,
                "failed": failed,
                "success_rate": f"{(success/total*100):.1f}%" if total > 0 else "0%"
            },
            "results": [r.to_dict() for r in self.results]
        }
    
    def save_report(self, output_path: Optional[str] = None) -> str:
        """
        保存测试报告
        
        Args:
            output_path: 输出路径（默认自动生成）
            
        Returns:
            保存的文件路径
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"test_reports/batch_report_{timestamp}.json"
        
        # 确保目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path


# 便捷函数
def quick_test(template_id: str, image_uuid: Optional[str] = None) -> TemplateTestResult:
    """快速测试单个模板"""
    runner = TemplateTestRunner(image_uuid=image_uuid)
    return runner.test_template(template_id)


def quick_batch(template_ids: List[str], image_uuid: Optional[str] = None) -> List[TemplateTestResult]:
    """快速批量测试"""
    runner = TemplateTestRunner(image_uuid=image_uuid)
    
    def on_start(tid, curr, total):
        print(f"[{curr}/{total}] Testing {tid}...")
    
    def on_complete(result):
        status = "✅" if result.success else "❌"
        print(f"  {status} {result.template_id}: {result.result_type or result.error}")
    
    return runner.test_batch(template_ids, on_start, on_complete)
