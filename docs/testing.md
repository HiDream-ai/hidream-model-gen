# 测试指南

Vivago AI Skill 多层级测试框架使用指南

---

## 测试架构

本项目采用 **5层测试架构**，平衡测试覆盖率与API调用成本：

```
Tier 1: 单元测试 (Mock, 0积分)     → 每次提交运行
Tier 2: 组件集成 (16积分)           → 每日运行
Tier 3: 核心功能 (106积分)          → 版本发布前
Tier 4: 端口采样 (168积分)          → 每周运行
Tier 5: 模板采样 (30积分/模板)      → 按需运行
```

---

## 最新测试状态 (2026-03-07)

✅ **全部测试通过** - 详见 [TEST_REPORT_2026_03_07.md](TEST_REPORT_2026_03_07.md)

| 层级 | 测试项 | 通过 | 积分 | 状态 |
|------|--------|------|------|------|
| Tier 1 | 单元测试 | 6 | 0 | ✅ |
| Tier 2 | 组件集成 | 4 | 16 | ✅ |
| Tier 3 | 核心功能 | 6 | 106 | ✅ |
| Tier 4 | 端口采样 | 8 | 168 | ✅ |
| Tier 5 | 模板采样 | 14 | 420 | ✅ |
| **总计** | | **38** | **710+** | **100%** |

---

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Token
```

### 2. 运行 Tier 1 单元测试

```bash
# 零成本，使用 Mock
python tests/tier1_report.py
```

### 3. 运行 Tier 2-3 图片测试

```bash
# 流水线测试，可顺序执行
python tests/tier2_integration.py
python tests/tier3_image.py
```

### 4. 运行视频功能测试

```bash
# 视频测试必须单独运行（避免超时扣积分）
python tests/video_img2vid.py
python tests/video_txt2vid.py
python tests/video_keyframe.py
```

---

## 交互式测试工具

### 智能测试运行器

```bash
python tests/run_optimized_tests.py
```

功能菜单：
- 显示所有测试及积分消耗
- 根据风险推荐测试
- 自动计算性价比
- 管理测试历史

### 查看测试历史

```bash
python tests/view_test_history.py
```

功能：
- 查看覆盖率报告
- 查看风险功能列表
- 查看推荐测试列表
- 记录新的测试结果

### 智能测试优化

```bash
python tests/smart_test_optimizer.py
```

根据风险等级、覆盖率和积分成本，自动推荐最优测试组合。

---

## 测试文件说明

### Tier 1 - 单元测试

| 文件 | 说明 | 积分 |
|------|------|------|
| `test_tier1_unit.py` | Mock-based单元测试 | 0 |

测试内容：
- VivagoClient 初始化
- 配置管理器
- 模板管理器
- 异常体系
- 类型系统

### Tier 2 - 组件集成

| 文件 | 说明 | 积分 |
|------|------|------|
| `test_tier2_integration.py` | 组件集成测试 | 16 |

测试内容：
- 配置加载
- 模板加载
- 缓存操作
- 图片上传

### Tier 3 - 核心功能

| 文件 | 说明 | 积分 |
|------|------|------|
| `test_tier3_image.py` | 图片功能流水线 | 16 |
| `video_img2vid.py` | 图生视频（单独） | 20 |
| `video_txt2vid.py` | 文生视频（单独） | 20 |
| `video_keyframe.py` | 视频首尾帧（单独） | 20 |
| `video_template.py` | 视频模板（单独） | 30 |

### Tier 4 - 端口采样

| 文件 | 说明 | 积分 |
|------|------|------|
| `test_tier4_image_ports.py` | 图片端口流水线 | 28 |
| `tier4_video_v3l.py` | v3L视频端口 | 60 |
| `tier4_video_kling.py` | Kling视频端口 | 80 |

### Tier 5 - 模板采样

| 目录 | 说明 | 积分 |
|------|------|------|
| `tier5_templates/` | 单个模板测试文件 | 30/个 |

---

## 测试原则

### 1. 图片功能 → 流水线测试

图片功能测试速度快，可以顺序执行：

```bash
pytest tests/test_tier3_image.py -v        # 16积分
pytest tests/test_tier4_image_ports.py -v   # 28积分
```

### 2. 视频功能 → 单独测试

视频功能耗时长且易超时，必须单独运行：

```bash
# ❌ 不要这样
pytest tests/video_*.py

# ✅ 应该这样
python tests/video_img2vid.py
# 等待完成
python tests/video_txt2vid.py
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
    """测试新端口 - X积分"""
    print(f'\n🔌 测试新端口 - X积分...')
    
    result = self.client.text_to_image(
        prompt='test prompt',
        port='new-port',
        batch_size=1
    )
    
    assert result is not None
    self.cache.save_test_result('port_new', {'status': 'success'})
    print('   ✅ 通过')
```

### 添加视频功能测试

创建新文件 `tests/video_new_feature.py`：

```python
#!/usr/bin/env python3
"""
新视频功能测试
积分: XX
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from dotenv import load_dotenv
load_dotenv()

from vivago_client import create_client

print('='*60)
print('视频测试: 新功能')
print('积分: XX')
print('='*60)

client = create_client()

print('\n⏳ 开始生成...')
result = client.new_feature(...)

print('\n✅ 成功!')
```

---

## 测试报告

最新完整测试报告：`TEST_REPORT.md`

包含：
- 测试执行摘要
- 详细测试结果
- Bug修复记录
- 覆盖率分析
- 积分消耗明细

历史测试报告：`docs/archive/`

---

## 注意事项

⚠️ **视频测试会消耗大量积分**：
- v3L: 20积分/次
- v3Pro: 30积分/次
- Kling video: 80积分/次

⚠️ **视频生成需要时间**：
- 预计 2-5 分钟/视频
- API队列可能延长等待时间

⚠️ **避免超时导致积分浪费**：
- 视频测试必须单独运行
- 不要批量运行视频测试
- 耐心等待，不要中断

---

## 参考文档

- [测试策略](TESTING_STRATEGY.md) - 原始测试策略
- [优化后策略](TEST_STRATEGY_OPTIMIZED.md) - 智能优化策略
- [积分定价](CREDITS_PRICING.md) - 各功能积分消耗
- [测试报告](../../TEST_REPORT.md) - 最新测试结果

---

*最后更新: 2026-03-07*
