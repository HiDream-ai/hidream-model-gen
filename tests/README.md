# 测试指南

Vivago AI Skill 多层级测试框架

---

## 测试层级架构

```
Tier 1: 单元测试 (Mock, 0积分)
├── test_tier1_unit.py

Tier 2: 组件集成 (16积分)
├── test_tier2_integration.py

Tier 3: 核心功能 (106积分)
├── test_tier3_image.py          # 图片功能流水线
├── video_img2vid.py             # 图生视频 (单独)
├── video_txt2vid.py             # 文生视频 (单独)
├── video_keyframe.py            # 视频首尾帧 (单独)
└── video_template.py            # 视频模板 (单独)

Tier 4: 端口采样 (168积分)
├── test_tier4_image_ports.py    # 图片端口流水线
├── tier4_video_v3l.py           # v3L视频端口 (单独)
└── tier4_video_kling.py         # Kling视频端口 (单独)

Tier 5: 模板采样 (30积分/模板)
└── tier5_templates/             # 单个模板测试文件

工具脚本
├── test_history_manager.py      # 测试历史记录
├── smart_test_optimizer.py      # 智能测试优化器
├── view_test_history.py         # 历史查询工具
└── generate_tier5_tests.py      # 生成模板测试
```

---

## 快速开始

### 运行单元测试 (Tier 1)

```bash
python -m pytest tests/test_tier1_unit.py -v
```

### 运行图片功能测试 (Tier 3)

```bash
python -m pytest tests/test_tier3_image.py -v
```

### 运行视频功能测试 (单独运行)

```bash
# 图生视频
python tests/video_img2vid.py

# 文生视频
python tests/video_txt2vid.py

# 视频首尾帧
python tests/video_keyframe.py

# 视频模板
python tests/video_template.py
```

### 运行端口测试 (Tier 4)

```bash
# 图片端口流水线
python -m pytest tests/test_tier4_image_ports.py -v

# v3L视频端口
python tests/tier4_video_v3l.py

# Kling视频端口 (高积分)
python tests/tier4_video_kling.py
```

---

## 交互式测试运行器

```bash
python tests/run_optimized_tests.py
```

功能：
- 显示所有可用测试
- 显示每个测试的积分消耗
- 根据风险推荐测试
- 管理测试历史

---

## 查看测试历史

```bash
python tests/view_test_history.py
```

功能：
- 查看完整覆盖率报告
- 查看风险功能列表
- 查看推荐测试列表
- 记录新的测试结果

---

## 智能测试优化

```bash
python tests/smart_test_optimizer.py
```

根据风险等级、覆盖率和积分成本，自动推荐最优测试组合。

---

## 测试配置

### 环境变量

创建 `.env` 文件：

```bash
HIDREAM_TOKEN=your_token
```

> **Note:** `STORAGE_AK` and `STORAGE_SK` are no longer required for testing.

### 测试图片

放置测试图片到 `tests/fixtures/images/`：
- `portrait.jpg` - 人像照片（主测试图）
- `landscape.jpg` - 风景照片
- `product.jpg` - 产品照片

---

## 测试原则

### 1. 图片功能 - 流水线测试
图片功能测试速度快，可以顺序执行：
```bash
pytest tests/test_tier3_image.py -v
```

### 2. 视频功能 - 单独测试
视频功能耗时长，必须单独运行：
```bash
python tests/video_xxx.py  # 一次一个
```

### 3. 积分管理
- 每次测试前显示预估积分
- 高积分测试（>50）需要确认
- 使用历史记录避免重复测试

---

## 添加新测试

### 添加图片端口测试

编辑 `tests/test_tier4_image_ports.py`：

```python
def test_port_new_port(self):
    """测试新端口"""
    result = self.client.text_to_image(
        prompt='test prompt',
        port='new-port',
        batch_size=1
    )
    assert result is not None
```

### 添加视频功能测试

创建新文件 `tests/video_new_feature.py`：

```python
#!/usr/bin/env python3
"""新视频功能测试"""
import sys
sys.path.insert(0, '../scripts')

from vivago_client import create_client

client = create_client()
result = client.new_video_function(...)
```

---

## 测试报告

最新测试报告：`TEST_REPORT.md`

包含：
- 测试执行摘要
- 详细测试结果
- Bug修复记录
- 覆盖率分析
- 积分消耗明细

---

## 注意事项

⚠️ **视频测试会消耗大量积分**：
- v3L: 20积分/次
- v3Pro: 30积分/次
- Kling video: 80积分/次

⚠️ **视频生成需要时间**：
- 预计 2-5 分钟/视频
- API队列可能延长等待时间

---

*最后更新: 2026-03-07*
