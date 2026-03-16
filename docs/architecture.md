# 架构设计

## 整体架构

```
Vivago AI Skill
├── 客户端层 (Client Layer)
│   ├── VivagoClient (V1 - 原始实现)
│   └── VivagoClientV2 (V2 - 组件化实现) ⭐推荐
│
├── 组件层 (Component Layer)
│   ├── ConfigManager    # 配置管理
│   ├── TaskPoller       # 任务轮询
│   ├── ImageUploader    # 图片上传
│   └── TemplateManager  # 模板管理
│
├── 工具层 (Utility Layer)
│   ├── types.py         # 类型定义
│   ├── exceptions.py    # 异常体系
│   └── config.py        # 全局配置
│
└── 接口层 (API Layer)
    ├── 文生图 (Text-to-Image)
    ├── 图生视频 (Image-to-Video)
    ├── 文生视频 (Text-to-Video)
    ├── 图生图 (Image-to-Image)
    ├── 视频模板 (Template-to-Video)
    └── 视频首尾帧 (Keyframe-to-Video)
```

## 设计原则

### 1. 单一职责原则 (SRP)

每个组件只负责一件事：

- **TaskPoller**: 只负责轮询任务状态
- **ImageUploader**: 只负责图片上传
- **ConfigManager**: 只负责配置管理

### 2. 开闭原则 (OCP)

对扩展开放，对修改关闭：

```python
# 添加新的生成功能，不需要修改现有代码
class NewGenerator:
    def generate(self, ...):
        pass

# 客户端自动支持
client.register_generator("new_feature", NewGenerator())
```

### 3. 依赖倒置原则 (DIP)

高层模块不依赖低层模块，都依赖抽象：

```python
# 好的设计
class VivagoClientV2:
    def __init__(self, poller: TaskPoller, uploader: ImageUploader):
        self.poller = poller
        self.uploader = uploader
```

## 关键决策记录 (ADR)

### ADR-1: 层级端口架构

**状态**: 已接受  
**日期**: 2026-03-05

**背景**: Vivago API有多个模型和端点，需要清晰的组织方式。

**决策**: 采用两级架构
- 一级功能: text_to_image, image_to_video 等
- 二级端口: kling-image, v3Pro 等具体配置

**后果**:
- ✅ 清晰的API组织
- ✅ 易于添加新端口
- ⚠️ 配置复杂度增加

### ADR-2: 组件化重构

**状态**: 已接受  
**日期**: 2026-03-06

**背景**: VivagoClient类过于庞大(1000+行)，难以维护。

**决策**: 拆分为独立组件
- TaskPoller: 轮询逻辑
- ImageUploader: 上传逻辑
- ConfigManager: 配置管理

**后果**:
- ✅ 代码更清晰
- ✅ 易于测试
- ✅ 可复用组件
- ⚠️ 需要维护两套API(V1和V2)

### ADR-3: 统一配置源

**状态**: 已接受  
**日期**: 2026-03-06

**背景**: api_ports.json和templates_data.json内容重复。

**决策**: templates_data.json作为唯一数据源

**后果**:
- ✅ 单一数据源
- ✅ 减少配置漂移
- ⚠️ 需要重构现有代码

## 数据流

### 文生图流程

```
User Input
    ↓
VivagoClient.text_to_image()
    ↓
Build Payload
    ↓
POST /v3/image/image_gen_kling/async
    ↓
Get Task ID
    ↓
TaskPoller.poll()
    ↓
GET /v3/image/txt2img/async/results
    ↓
Return Results
```

### 图生视频流程

```
User Image
    ↓
ImageUploader.upload()
    ↓
Resize + Compress
    ↓
Upload to S3
    ↓
Get UUID (j_xxxx)
    ↓
VivagoClient.image_to_video()
    ↓
POST /v3/video/video_diffusion/async
    ↓
TaskPoller.poll()
    ↓
Return Video URL
```

## 错误处理策略

### 异常层次

```
VivagoError (基类)
├── ConfigurationError
│   ├── MissingCredentialError
│   └── InvalidConfigurationError
├── APIError
│   ├── NetworkError
│   ├── TimeoutError
│   └── RateLimitError
├── TaskError
│   ├── TaskFailedError
│   ├── TaskRejectedError
│   └── TaskTimeoutError
└── ...
```

### 重试策略

| 错误类型 | 重试 | 说明 |
|---------|------|------|
| NetworkError | ✅ 3次 | 指数退避 |
| TimeoutError | ✅ 3次 | 固定间隔 |
| RateLimitError | ✅ 按header | 遵守Retry-After |
| TaskFailedError | ❌ | 立即失败 |
| TaskRejectedError | ❌ | 立即失败 |

## 性能考虑

### 图片上传
- 自动压缩到1024px
- JPEG质量95%
- 最大5MB

### 任务轮询
- 默认3秒间隔
- 最大60次尝试
- 支持超时取消

### 连接池
```python
# requests 使用连接池
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('https://', adapter)
```
