# 故障排查

## 常见问题

### 1. 认证错误

**错误**: `MissingCredentialError: Missing required credential: HIDREAM_TOKEN`

**解决**:
```bash
# 检查环境变量
echo $HIDREAM_TOKEN

# 如果不存在，设置它
export HIDREAM_TOKEN="your_token_here"

# 或者创建.env文件
cp .env.example .env
# 编辑.env填入凭证
```

### 2. 图片上传失败

**错误**: `ImageUploadError: Failed to upload image`

**排查**:
```python
# 检查 token 是否有效
export HIDREAM_TOKEN="your_vivago_api_token"

# 检查图片存在
ls -la /path/to/image.jpg

# 检查图片格式
file /path/to/image.jpg
```

**常见原因**:
- API token 过期或无效
- 网络问题
- 图片格式不支持 (仅支持 JPEG/PNG)
- 图片过大 (建议不超过 5MB)

**注意**: 从 v0.4.0 开始，图片上传不再需要 STORAGE_AK/SK。如果仍然需要旧的上传方式，请使用 `upload_image_legacy()` 方法（已废弃）。

### 3. 任务超时

**错误**: `TaskTimeoutError: Task did not complete after 180s`

**解决**:
```python
# 增加轮询次数
from scripts.task_poller import TaskPoller

poller = TaskPoller(client, max_attempts=120)  # 默认60
result = poller.poll(task_id, endpoint)

# 或使用更长的超时
result = poller.poll_with_timeout(task_id, endpoint, timeout_seconds=600)
```

### 4. 内容被拒绝

**错误**: `TaskRejectedError: Content policy violation`

**原因**:
- 提示词包含敏感内容
- 图片包含不当内容

**解决**:
- 修改提示词
- 更换输入图片
- 查看Vivago内容政策

### 5. 网络错误

**错误**: `NetworkError: Connection timeout`

**排查**:
```bash
# 测试网络连接
ping vivago.ai

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 测试API可达
curl -I https://vivago.ai/api/gw/v3/image/txt2img/async
```

**解决**:
- 检查网络连接
- 配置代理（如需要）
- 增加超时时间

### 6. 模板不存在

**错误**: `InvalidPortError: Invalid port: invalid_template`

**排查**:
```python
from scripts.template_manager import get_template_manager

manager = get_template_manager()
print(manager.list_templates())  # 查看所有模板
```

**常见模板ID**:
- `ghibli` - 吉卜力风格
- `iron_man` - 钢铁侠
- `renovation_old_photos` - 老照片修复

### 7. 内存不足

**错误**: `MemoryError` 或进程被杀死

**解决**:
```python
# 减少批量大小
results = client.text_to_image(prompt="test", batch_size=1)  # 不是4

# 处理大图片前先压缩
from PIL import Image
img = Image.open("large.jpg")
img.thumbnail((1024, 1024))
img.save("compressed.jpg")
```

## 调试技巧

### 启用详细日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('scripts.vivago_client').setLevel(logging.DEBUG)
```

### 查看原始API响应

```python
import json

# 在调用后打印响应
response = client._post(endpoint, payload)
print(json.dumps(response, indent=2))
```

### 测试连接

```python
# 测试文生图（最简单）
try:
    results = client.text_to_image(
        prompt="a red circle",
        port="kling-image",
        batch_size=1
    )
    print("✅ 连接正常")
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

## 获取帮助

### 查看日志

```bash
# 最近的Git提交
git log --oneline -5

# 查看特定文件历史
git log --oneline -- scripts/vivago_client.py
```

### 检查版本

```python
# 在Python中
import scripts
print(scripts.__version__)  # 如果有的话

# 查看requirements
cat requirements.txt
```

## 报告问题

提交Issue时包含：

1. **环境信息**:
   - Python版本: `python --version`
   - 操作系统
   - 库版本: `pip list | grep -E "requests|boto3"`

2. **错误信息**:
   - 完整错误堆栈
   - 触发代码

3. **重现步骤**:
   - 最小可复现代码

4. **预期 vs 实际**:
   - 你期望发生什么
   - 实际发生了什么

```markdown
## 环境
- Python: 3.10.0
- OS: Ubuntu 22.04
- vivago-ai-skill: main branch

## 错误
```
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    client.text_to_image(prompt="test")
Exception: ...
```

## 重现代码
```python
from scripts.vivago_client import create_client
client = create_client()
client.text_to_image(prompt="test")
```

## 预期
成功生成图片

## 实际
抛出异常
```
