#!/usr/bin/env python3
"""
Vivago AI 自定义异常体系
统一错误处理，提供清晰的错误分类
"""


class VivagoError(Exception):
    """Vivago API 基础异常"""
    pass


# ==================== 配置错误 ====================

class ConfigurationError(VivagoError):
    """配置相关错误"""
    pass


class MissingCredentialError(ConfigurationError):
    """缺少必要凭证"""
    def __init__(self, credential_name: str):
        super().__init__(f"Missing required credential: {credential_name}")
        self.credential_name = credential_name


class InvalidConfigurationError(ConfigurationError):
    """配置无效"""
    pass


# ==================== API 错误 ====================

class APIError(VivagoError):
    """API 调用错误"""
    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class NetworkError(APIError):
    """网络连接错误"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class TimeoutError(APIError):
    """请求超时"""
    def __init__(self, message: str, timeout_seconds: float = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class RateLimitError(APIError):
    """速率限制"""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


# ==================== 任务错误 ====================

class TaskError(VivagoError):
    """任务执行错误"""
    pass


class TaskFailedError(TaskError):
    """任务执行失败"""
    def __init__(self, task_id: str, reason: str = None):
        super().__init__(f"Task {task_id} failed" + (f": {reason}" if reason else ""))
        self.task_id = task_id
        self.reason = reason


class TaskRejectedError(TaskError):
    """任务被内容审核拒绝"""
    def __init__(self, task_id: str, reason: str = "Content policy violation"):
        super().__init__(f"Task {task_id} rejected: {reason}")
        self.task_id = task_id
        self.reason = reason


class TaskTimeoutError(TaskError):
    """任务等待超时"""
    def __init__(self, task_id: str, waited_seconds: float):
        super().__init__(f"Task {task_id} did not complete after {waited_seconds}s")
        self.task_id = task_id
        self.waited_seconds = waited_seconds


# ==================== 模板错误 ====================

class TemplateError(VivagoError):
    """模板相关错误"""
    pass


class TemplateNotFoundError(TemplateError):
    """模板不存在"""
    def __init__(self, template_id: str):
        super().__init__(f"Template not found: {template_id}")
        self.template_id = template_id


class TemplateNotTestedError(TemplateError):
    """模板未测试"""
    def __init__(self, template_id: str):
        super().__init__(f"Template {template_id} has not been tested")
        self.template_id = template_id


# ==================== 端口错误 ====================

class PortError(VivagoError):
    """端口配置错误"""
    pass


class InvalidPortError(PortError):
    """无效端口"""
    def __init__(self, port: str, category: str = None, available_ports: list = None):
        msg = f"Invalid port: {port}"
        if category:
            msg += f" for category {category}"
        if available_ports:
            msg += f". Available: {', '.join(available_ports)}"
        super().__init__(msg)
        self.port = port
        self.category = category
        self.available_ports = available_ports


class InvalidCategoryError(PortError):
    """无效类别"""
    def __init__(self, category: str, available_categories: list = None):
        msg = f"Invalid category: {category}"
        if available_categories:
            msg += f". Available: {', '.join(available_categories)}"
        super().__init__(msg)
        self.category = category
        self.available_categories = available_categories


# ==================== 图片错误 ====================

class ImageError(VivagoError):
    """图片处理错误"""
    pass


class ImageUploadError(ImageError):
    """图片上传失败"""
    def __init__(self, message: str, file_path: str = None):
        super().__init__(message)
        self.file_path = file_path


class ImageTooLargeError(ImageError):
    """图片太大"""
    def __init__(self, file_path: str, size_mb: float, max_size_mb: float):
        super().__init__(f"Image {file_path} is {size_mb:.1f}MB (max {max_size_mb}MB)")
        self.file_path = file_path
        self.size_mb = size_mb
        self.max_size_mb = max_size_mb


# ==================== 工具函数 ====================

def raise_for_status(result: dict, task_id: str = None):
    """
    根据API返回状态抛出相应异常
    
    Args:
        result: API返回的结果字典
        task_id: 任务ID（可选）
    """
    code = result.get('code', -1)
    
    if code == 0:
        return  # 成功
    
    message = result.get('msg', 'Unknown error')
    
    # 根据错误码分类
    if code == 403 or 'content' in message.lower() or 'policy' in message.lower():
        raise TaskRejectedError(task_id or "unknown", message)
    elif code >= 500:
        raise APIError(f"Server error: {message}", status_code=code, response_body=result)
    else:
        raise APIError(f"API error: {message}", status_code=code, response_body=result)
