# API参考

## VivagoClient

### 初始化

```python
from scripts.vivago_client import create_client

# 从环境变量读取凭证
client = create_client()

# 或者显式传入 token
client = create_client(token="your_token")

# 注意: storage_ak 和 storage_sk 参数已废弃，仅在调用 upload_image_legacy() 时需要
```

### 图片上传

```python
# 上传本地图片
image_uuid = client.upload_image("/path/to/image.jpg")

# 或者使用 v2 方法（显式指定）
image_uuid = client.upload_image_v2("/path/to/image.jpg")

# 旧方法（已废弃，需要 STORAGE_AK/SK）
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    image_uuid = client.upload_image_legacy("/path/to/image.jpg")
```

### 文生图 (text_to_image)

```python
results = client.text_to_image(
    prompt="描述文本",           # 必需
    port="kling-image",          # 可选，默认kling-image
    wh_ratio="1:1",              # 可选，默认1:1
    batch_size=1,                # 可选，默认1，范围1-4
    style="default",             # 可选
    seed=-1                      # 可选，随机种子
)
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | str | ✅ | 图像描述 |
| port | str | ❌ | 模型端口 |
| wh_ratio | str | ❌ | 宽高比 |
| batch_size | int | ❌ | 生成数量 |
| style | str | ❌ | 风格 |
| seed | int | ❌ | 随机种子 |

**wh_ratio选项**: "1:1", "16:9", "9:16", "4:3", "3:4"

**port选项**: "kling-image", "hidream-txt2img", "nano-banana"

**返回**:
```python
[
    {
        "task_id": "uuid",
        "task_status": 1,
        "result": ["url1", "url2"]
    }
]
```

### 图生视频 (image_to_video)

```python
results = client.image_to_video(
    prompt="视频描述",           # 必需
    image_uuid="j_xxxx",         # 必需，图片UUID
    port="v3Pro",                # 可选，默认v3Pro
    wh_ratio="1:1",              # 可选
    duration=5,                  # 可选，默认5，可选5或10
    mode="Slow"                  # 可选，默认Slow，可选Fast/Slow
)
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | str | ✅ | 视频描述 |
| image_uuid | str | ✅ | 图片UUID |
| port | str | ❌ | 模型端口 |
| wh_ratio | str | ❌ | 宽高比 |
| duration | int | ❌ | 时长(秒) |
| mode | str | ❌ | 模式 |

**port选项**: "v3Pro", "v3L", "kling-video"

### 视频模板 (template_to_video)

```python
results = client.template_to_video(
    image_uuid="j_xxxx",         # 必需
    template="ghibli",           # 必需，模板ID
    wh_ratio="1:1"               # 可选
)
```

**热门模板**:

| 模板ID | 说明 |
|--------|------|
| ghibli | 吉卜力风格 |
| iron_man | 钢铁侠装甲 |
| angel_wings | 天使翅膀 |
| magic_reveal_ravenclaw | 拉文克劳魔法 |
| renovation_of_old_photos | 老照片修复 |

查看所有模板：
```python
from scripts.template_manager import get_template_manager

manager = get_template_manager()
templates = manager.list_templates()
for tid, name in templates.items():
    print(f"{tid}: {name}")
```

### 图片上传 (upload_image)

```python
image_uuid = client.upload_image(
    "/path/to/image.jpg"    # 本地图片路径
)
# 返回: "j_xxxxx"
```

**自动处理**:
- 压缩到1024px
- JPEG格式
- 最大5MB

### 图生图 (image_to_image)

```python
results = client.image_to_image(
    prompt="融合风格描述",         # 必需
    image_uuids=["p_xxxx"],        # 必需，图片UUID列表
    port="kling-image",            # 可选，默认kling-image
    strength=0.8,                  # 可选，变化强度0-1
    relevance=[0.9],               # 可选，每张图的参考权重
    wh_ratio="1:1"                 # 可选
)
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | str | ✅ | 图像描述 |
| image_uuids | list | ✅ | 图片UUID列表 |
| port | str | ❌ | 模型端口 |
| strength | float | ❌ | 变化强度(0-1) |
| relevance | list | ❌ | 参考权重列表 |
| wh_ratio | str | ❌ | 宽高比 |

**⚠️ 重要：UUID 格式规范**

Vivago 平台使用以下格式的 UUID：

| 类型 | 格式示例 | 说明 |
|------|----------|------|
| **上传图片** | `j_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | 上传后的图片 |
| **生成图片** | `p_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | 文生图结果 |
| **生成视频** | `v_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | 视频结果 |

**正确格式**:
```python
# ✅ 正确：完整的 UUID
image_uuids = [
    "p_26d2197b-9da8-4cd6-a965-d7eb8e63f846",  # 杰尼龟
    "p_929c4dd4-a08b-4d04-b4c5-6f376ced439e",  # 妙蛙种子
]

# ❌ 错误：简写或自定义ID
image_uuids = ["p_pikachu", "p_squirtle"]  # 会导致失败
```

**多图融合示例**:
```python
# 四只宝可梦融合
results = client.image_to_image(
    prompt="A fusion creature combining four Pokemon",
    image_uuids=[
        "p_26d2197b-9da8-4cd6-a965-d7eb8e63f846",  # 杰尼龟
        "p_929c4dd4-a08b-4d04-b4c5-6f376ced439e",  # 妙蛙种子
        "p_54fca3b0-b203-4ad7-a014-1db7ac36fd51",  # 小火龙
        "p_xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",      # 皮卡丘(需先生成)
    ],
    port="kling-image",
    strength=0.7,
    relevance=[0.9, 0.9, 0.9, 0.9]
)
```

**port选项**: "kling-image"(快), "nano-banana"(质)

## 任务状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 0 | 等待中 | 任务已提交 |
| 1 | 已完成 | 可以获取结果 |
| 2 | 处理中 | 正在生成 |
| 3 | 失败 | 生成失败 |
| 4 | 被拒绝 | 内容审核未通过 |

## 异常处理

```python
from scripts.exceptions import (
    TaskFailedError,
    TaskRejectedError,
    NetworkError
)

try:
    results = client.text_to_image(prompt="test")
except TaskRejectedError as e:
    print(f"内容被拒绝: {e.reason}")
except TaskFailedError as e:
    print(f"任务失败: {e.reason}")
except NetworkError as e:
    print(f"网络错误: {e}")
```

## 高级用法

### 批量生成

```python
# 一次生成4张图
results = client.text_to_image(
    prompt="风景",
    batch_size=4
)
```

### 自定义轮询

```python
from scripts.task_poller import TaskPoller

poller = TaskPoller(client, max_attempts=30, retry_delay=5)

result = poller.poll(
    task_id="xxx",
    result_endpoint="/v3/video/...",
    on_progress=lambda attempt, max: print(f"{attempt}/{max}"),
    on_complete=lambda data: print("完成！"),
    on_fail=lambda err: print(f"失败: {err}")
)
```

### 使用V2客户端

```python
from scripts.vivago_client_v2 import create_client_v2

client = create_client_v2()
# API与V1相同，但内部架构更优
results = client.text_to_image(prompt="test")
```
