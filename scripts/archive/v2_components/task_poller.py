#!/usr/bin/env python3
"""
任务轮询器 - 处理异步任务状态轮询
"""
import time
import logging
from typing import Optional, Callable, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """任务状态"""
    PENDING = 0
    COMPLETED = 1
    PROCESSING = 2
    FAILED = 3
    REJECTED = 4


class TaskPoller:
    """
    异步任务轮询器
    
    职责：
    1. 轮询任务状态
    2. 处理超时逻辑
    3. 提供进度回调
    """
    
    def __init__(
        self,
        client,
        max_attempts: int = 60,
        retry_delay: int = 3
    ):
        """
        初始化轮询器
        
        Args:
            client: VivagoClient实例
            max_attempts: 最大轮询次数
            retry_delay: 轮询间隔（秒）
        """
        self.client = client
        self.max_attempts = max_attempts
        self.retry_delay = retry_delay
    
    def poll(
        self,
        task_id: str,
        result_endpoint: str,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_fail: Optional[Callable[[str], None]] = None,
        on_reject: Optional[Callable[[str], None]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        轮询任务直到完成或失败
        
        Args:
            task_id: 任务ID
            result_endpoint: 结果查询端点
            on_progress: 进度回调(current_attempt, max_attempts)
            on_complete: 完成回调(result_data)
            on_fail: 失败回调(error_message)
            on_reject: 拒绝回调(reason)
            
        Returns:
            成功时返回结果数据，失败返回None
        """
        for attempt in range(1, self.max_attempts + 1):
            if on_progress:
                on_progress(attempt, self.max_attempts)
            
            time.sleep(self.retry_delay)
            
            try:
                response = self.client.get_result(task_id, result_endpoint)
            except Exception as e:
                logger.warning(f"Poll error for {task_id}: {e}")
                continue
            
            if not response:
                continue
            
            code = response.get('code', -1)
            if code != 0:
                logger.debug(f"Task {task_id} not ready, code={code}")
                continue
            
            result_data = response.get('result', {})
            sub_results = result_data.get('sub_task_results', [])
            
            if not sub_results:
                continue
            
            task_info = sub_results[0]
            status = task_info.get('task_status', 0)
            state = TaskState(status)
            
            if state == TaskState.COMPLETED:
                if on_complete:
                    on_complete(task_info)
                return task_info
            
            elif state == TaskState.FAILED:
                error = task_info.get('error', 'Unknown error')
                logger.error(f"Task {task_id} failed: {error}")
                if on_fail:
                    on_fail(error)
                return None
            
            elif state == TaskState.REJECTED:
                reason = "Content policy violation"
                logger.warning(f"Task {task_id} rejected: {reason}")
                if on_reject:
                    on_reject(reason)
                return None
        
        # 超时
        logger.error(f"Task {task_id} timeout after {self.max_attempts * self.retry_delay}s")
        return None
    
    def poll_with_timeout(
        self,
        task_id: str,
        result_endpoint: str,
        timeout_seconds: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        带超时的简单轮询
        
        Args:
            task_id: 任务ID
            result_endpoint: 结果查询端点
            timeout_seconds: 超时时间（秒）
            
        Returns:
            成功时返回结果数据，超时返回None
        """
        max_attempts = timeout_seconds // self.retry_delay
        original_max = self.max_attempts
        self.max_attempts = max_attempts
        
        try:
            return self.poll(task_id, result_endpoint)
        finally:
            self.max_attempts = original_max
