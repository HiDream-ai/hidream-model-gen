# 快速开始

## 安装

```bash
# 克隆仓库
git clone https://github.com/ZhaofanQiu/vivago-ai-skill.git
cd vivago-ai-skill

# 安装依赖
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 填入你的凭证
```

## 基础用法

### 文生图

```python
from scripts.vivago_client import create_client

client = create_client()

# 使用 Kling O1 (快速)
results = client.text_to_image(
    prompt="一只可爱的小熊猫",
    port="kling-image",
    wh_ratio="1:1",
    batch_size=1
)

print(f"生成完成: {results}")
```

### 图生视频

```python
# 先上传图片
image_uuid = client.upload_image("/path/to/photo.jpg")

# 生成视频
results = client.image_to_video(
    prompt="熊猫慢慢转头",
    image_uuid=image_uuid,
    port="v3Pro",
    duration=5,
    mode="Slow"
)
```

### 视频模板

```python
results = client.template_to_video(
    image_uuid=image_uuid,
    template="ghibli",  # 吉卜力风格
    wh_ratio="9:16"
)
```

## 可用端口

### 文生图

| 端口 | 显示名称 | 速度 | 质量 |
|------|---------|------|------|
| `kling-image` | Kling O1 | 快 | 优秀 |
| `hidream-txt2img` | Vivago.ai 2.0 | 中等 | 良好 |
| `nano-banana` | Nano Banana 2 | 慢 | 极优 |

### 图生视频

| 端口 | 显示名称 | 速度 | 质量 |
|------|---------|------|------|
| `v3Pro` | Vivago.ai 2.0 | 慢 | 极优 |
| `v3L` | Vivago.ai 2.0 360p | 快 | 良好 |
| `kling-video` | Kling video O1 | 中等 | 极优 |

## 下一步

- 查看 [API参考](api_reference.md) 了解所有功能
- 查看 [测试指南](testing.md) 学习如何测试
- 查看 [故障排查](troubleshooting.md) 解决常见问题
