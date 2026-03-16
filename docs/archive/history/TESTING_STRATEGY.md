# Vivago AI Skill - 多层级高效测试方案

**设计目标**: 在最小化API调用成本的前提下，确保代码健康度和功能正确性  
**核心策略**: 分层级测试 + 智能采样 + 持久化缓存 + 按需触发
**更新日期**: 2026-03-07 (根据反馈更新)

---

## 一、测试层级架构

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: 静态/单元测试层 (零API成本)                           │
│  ├── 代码规范检查 (flake8, black)                             │
│  ├── 类型检查 (mypy)                                          │
│  ├── 单元测试 (pytest + Mock)                                  │
│  └── 覆盖率检查                                                │
│  成本: ¥0 | 时间: <1分钟 | 触发: 按需/代码变更                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: 组件集成测试层 (极低API成本)                          │
│  ├── 配置管理器验证                                            │
│  ├── 图片上传流程 (单次，复用缓存)                              │
│  └── 任务轮询机制 (Mock任务)                                   │
│  成本: ~¥0.1 | 时间: <2分钟 | 触发: 按需/配置变更              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: 核心功能冒烟测试层 (低API成本)                        │
│  ├── 文生图 (1个端口 × 1张)                                   │
│  ├── 图生视频 (1个端口 × 1张)                                 │
│  └── 模板视频 (1个模板 × 1张)                                 │
│  成本: ~¥2 | 时间: ~5分钟 | 触发: 按需/核心功能变更            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 4: 端口采样测试层 (中等API成本)                          │
│  ├── 每个algo_type采样1个代表端口                              │
│  ├── 同类端口共享测试结果                                      │
│  └── 使用持久化缓存图片UUID                                    │
│  成本: ~¥5-10 | 时间: ~15分钟 | 触发: 按需/新增端口            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 5: 模板全面测试层 (高API成本，智能采样)                   │
│  ├── 按类别采样 (每类1-2个代表)                               │
│  ├── 新/修改模板优先测试                                       │
│  └── 失败模板自动重测                                          │
│  成本: ~¥20-50 | 时间: ~1小时 | 触发: 按需/发布前/全面验证     │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、触发策略 (按需触发)

### 触发方式

| 触发方式 | 说明 | 适用层级 |
|---------|------|---------|
| **自动提醒** | AI根据代码变更程度推荐测试层级 | Tier 1-3 |
| **用户指定** | 用户明确指定进行某层测试 | Tier 1-5 |
| **智能检测** | 新增/修改端口或模板时提醒 | Tier 4-5 |

### 代码变更 → 测试层级映射

当代码发生变更时，AI将评估变更范围并推荐测试层级：

```
变更类型                          推荐测试层级
─────────────────────────────────────────────────────
文档修改 (README等)               Tier 0 (无需测试)
代码格式/注释                     Tier 0 (无需测试)
单元测试文件                      Tier 1 (静态测试)
工具函数/工具类                   Tier 1 (静态测试)
配置加载逻辑                      Tier 1+2 (静态+组件)
API客户端逻辑                     Tier 1+2+3 (静态+组件+核心)
新增/修改端口配置                 Tier 1+2+3+4 (到端口层)
新增/修改模板                     Tier 1+2+3+5 (到模板层)
架构重大变更                      Tier 1+2+3+4+5 (全量)
```

### 缓存管理

**持久化缓存策略**:
- 测试图片UUID: 永久缓存，直到手动清除
- 测试结果: 永久缓存，手动标记失效
- 失败记录: 永久保留，用于优先重测

**缓存清除指令**:
```
用户: "清除测试结果缓存"
AI: 清除 tests/fixtures/cache/test_results.json

用户: "清除图片UUID缓存"
AI: 清除 tests/fixtures/uuids.json，需重新上传

用户: "清除所有缓存"
AI: 清除所有缓存文件
```

---

## 一、测试层级架构

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: 静态/单元测试层 (零API成本)                           │
│  ├── 代码规范检查 (flake8, black)                             │
│  ├── 类型检查 (mypy)                                          │
│  ├── 单元测试 (pytest + Mock)                                  │
│  └── 覆盖率检查                                                │
│  成本: ¥0 | 时间: <1分钟 | 触发: 每次提交                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: 组件集成测试层 (极低API成本)                          │
│  ├── 配置管理器验证                                            │
│  ├── 图片上传流程 (单次)                                       │
│  └── 任务轮询机制 (Mock任务)                                   │
│  成本: ~¥0.1 | 时间: <2分钟 | 触发: 每日构建                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: 核心功能冒烟测试层 (低API成本)                        │
│  ├── 文生图 (1个端口 × 1张)                                   │
│  ├── 图生视频 (1个端口 × 1张)                                 │
│  └── 模板视频 (1个模板 × 1张)                                 │
│  成本: ~¥1-2 | 时间: ~5分钟 | 触发: 每日构建                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 4: 端口采样测试层 (中等API成本)                          │
│  ├── 每个algo_type采样1个代表端口                              │
│  ├── 同类端口共享测试结果                                      │
│  └── 使用缓存图片UUID减少上传成本                              │
│  成本: ~¥5-10 | 时间: ~15分钟 | 触发: 每周                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 5: 模板全面测试层 (高API成本，智能采样)                   │
│  ├── 按类别采样 (每类1-2个代表)                               │
│  ├── 新/修改模板优先测试                                       │
│  └── 失败模板自动重测                                          │
│  成本: ~¥20-50 | 时间: ~1小时 | 触发: 每周/发布前             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、详细测试策略

### Tier 1: 静态/单元测试 (零成本层)

**目标**: 验证代码质量和基础逻辑，不调用任何API

**测试内容**:
```python
# 1. 代码规范
test_code_quality.py
├── test_flake8_compliance()      # 代码风格
├── test_black_formatting()       # 格式统一
└── test_import_order()           # 导入排序

# 2. 类型检查  
test_type_check.py
├── test_client_type_hints()      # 客户端类型
├── test_config_types()           # 配置类型
└── test_response_types()         # 响应类型

# 3. 单元测试 (Mock)
test_unit.py
├── test_client_initialization()  # 初始化
├── test_port_validation()        # 端口验证
├── test_template_id_generation() # ID生成
├── test_exception_hierarchy()    # 异常体系
├── test_config_loading()         # 配置加载
├── test_poller_logic()           # 轮询逻辑
└── test_uploader_compression()   # 图片压缩
```

**Mock策略**:
```python
@pytest.fixture
def mock_vivago_api():
    """Mock所有API调用"""
    with responses.RequestsMock() as rsps:
        # Mock生成接口
        rsps.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/image_gen_kling/async',
            json={'code': 0, 'result': {'task_id': 'mock-123'}},
            status=200
        )
        # Mock结果查询
        rsps.add(
            responses.POST,
            'https://vivago.ai/api/gw/v3/image/txt2img/async/results',
            json={'code': 0, 'result': {'sub_task_results': [
                {'task_status': 1, 'result': ['http://mock/image.jpg']}
            ]}},
            status=200
        )
        yield rsps
```

**触发条件**: 每次提交自动运行
**成本**: ¥0
**时间**: <1分钟

---

### Tier 2: 组件集成测试 (极低成本层)

**目标**: 验证组件间协作，最小化真实API调用

**测试内容**:
```python
test_component_integration.py

# 1. 配置管理器 (零成本)
def test_config_manager_loading():
    """验证配置加载"""
    manager = get_config_manager()
    assert len(manager.list_ports()) > 0
    assert manager.get_port("kling-image") is not None

# 2. 图片上传 (单次，复用)
def test_image_upload_workflow():
    """测试上传流程，UUID缓存复用"""
    # 使用预设的测试图片UUID，避免重复上传
    test_uuid = get_test_image_uuid()  # 从缓存或环境变量
    assert test_uuid.startswith("j_")

# 3. 任务轮询 (Mock任务)
def test_poller_with_mock_task():
    """测试轮询逻辑，使用Mock任务ID"""
    poller = TaskPoller(mock_client)
    result = poller.poll("mock-task-id", "/v3/test/results")
    assert result is not None
```

**测试图片管理**:
```python
# tests/fixtures/test_assets.py
TEST_IMAGE_UUIDS = {
    "portrait": "j_xxx",      # 人像
    "landscape": "j_yyy",     # 风景
    "product": "j_zzz",       # 产品
}

def get_test_image(image_type="portrait"):
    """获取测试图片UUID，避免重复上传"""
    return TEST_IMAGE_UUIDS.get(image_type)
```

**触发条件**: 每日构建
**成本**: ~¥0.1 (仅一次上传验证)
**时间**: <2分钟

---

### Tier 3: 核心功能冒烟测试 (低成本层)

**目标**: 验证核心功能可用，每个大类只测最基本路径

**测试策略**: 
- 每个一级功能只测1个最简单的二级端口
- 使用最小参数 (batch_size=1, duration=5)
- 使用缓存的测试图片UUID

```python
test_smoke_core_features.py

class TestCoreFeaturesSmoke:
    """核心功能冒烟测试 - 每个功能只测最基本路径"""
    
    TEST_IMAGE_UUID = "j_cached_test_image"  # 预上传的测试图片
    
    def test_01_text_to_image(self):
        """文生图 - 只测最快的Kling"""
        result = client.text_to_image(
            prompt="a red circle",  # 最简单的提示词
            port="kling-image",     # 最快的端口
            batch_size=1            # 只生成1张
        )
        assert result is not None
        # 成本: ~¥0.1, 时间: ~10秒
    
    def test_02_image_to_video(self):
        """图生视频 - 只测v3L (360p最快)"""
        result = client.image_to_video(
            prompt="camera slowly zooming out",
            image_uuid=self.TEST_IMAGE_UUID,  # 复用缓存图片
            port="v3L",                        # 最快的端口
            duration=5                         # 最短时长
        )
        assert result is not None
        # 成本: ~¥0.5, 时间: ~2分钟
    
    def test_03_text_to_video(self):
        """文生视频 - 只测v3L"""
        result = client.text_to_video(
            prompt="a flower blooming",
            port="v3L",
            duration=5
        )
        assert result is not None
        # 成本: ~¥0.5, 时间: ~2分钟
    
    def test_04_image_to_image(self):
        """图生图 - 只测Kling"""
        result = client.image_to_image(
            prompt="convert to watercolor",
            image_uuids=[self.TEST_IMAGE_UUID],
            port="kling-image"
        )
        assert result is not None
        # 成本: ~¥0.1, 时间: ~10秒
    
    def test_05_keyframe_to_video(self):
        """视频首尾帧 - 使用相同图片测试"""
        result = client.keyframe_to_video(
            prompt="transform",
            start_image_uuid=self.TEST_IMAGE_UUID,
            end_image_uuid=self.TEST_IMAGE_UUID,  # 相同图片
            port="v3L",
            duration=5
        )
        assert result is not None
        # 成本: ~¥0.5, 时间: ~2分钟
    
    def test_06_template_to_video(self):
        """视频模板 - 只测1个最简单的模板"""
        result = client.template_to_video(
            image_uuid=self.TEST_IMAGE_UUID,
            template="renovation_old_photos",  # 最稳定的模板
            wh_ratio="1:1"
        )
        assert result is not None
        # 成本: ~¥0.5, 时间: ~2分钟
```

**成本估算**:
- 文生图 (Kling): ~¥0.1
- 图生视频 (v3L): ~¥0.5
- 文生视频 (v3L): ~¥0.5
- 图生图 (Kling): ~¥0.1
- 视频首尾帧 (v3L): ~¥0.5
- 视频模板 (基础): ~¥0.5

**总计**: ~¥2.2/次, 时间: ~8分钟

**触发条件**: 每日构建

---

### Tier 4: 端口采样测试 (中等成本层)

**目标**: 验证不同algo_type的端口可用性，同类端口只测代表

**采样策略**:
```python
# 按algo_type分组，每组只测1个代表
ALGO_TYPE_SAMPLES = {
    # 文生图
    "image_gen_kling": "kling-image",
    "txt2img": "hidream-txt2img",
    "image_gen_std": "nano-banana",
    
    # 图生视频
    "video_diffusion": "v3L",          # 代表v3L/v3Pro
    "video_diffusion_img2vid": "v3Pro", # img2vid专用
    "video_diffusion_gen2vid": "kling-video",
    
    # 视频模板 (按类型采样)
    "proto_transformer": "renovation_old_photos",
    "figure_transformer": "glam_cat",
    "outfit_transformer": "kiss_hand",
    "avatar_transformer": "barbie",
}
```

**测试实现**:
```python
test_port_sampling.py

class TestPortSampling:
    """端口采样测试 - 同类端口只测代表"""
    
    def test_sample_by_algo_type(self):
        """按algo_type采样测试"""
        results = {}
        
        for algo_type, sample_port in ALGO_TYPE_SAMPLES.items():
            try:
                # 根据类型选择合适的测试方法
                if "image" in algo_type:
                    result = test_image_port(sample_port)
                elif "video" in algo_type or "transformer" in algo_type:
                    result = test_video_port(sample_port)
                
                results[algo_type] = {"status": "PASS", "port": sample_port}
            except Exception as e:
                results[algo_type] = {"status": "FAIL", "error": str(e)}
        
        return results
```

**成本优化**:
- 同类端口共享结果 (v3L和v3Pro只测一个)
- 使用缓存图片UUID
- 批量测试时串行执行，避免并发费用

**成本估算**: ~¥5-10/次
**时间**: ~15分钟
**触发条件**: 每周

---

### Tier 5: 模板全面测试 (高成本层，智能采样)

**目标**: 验证所有模板可用性，使用智能采样减少测试量

**模板分类采样策略**:
```python
# 按功能类别采样，每类只测1-2个代表
TEMPLATE_CATEGORIES = {
    "style_transfer": ["ghibli", "1930s_vintage_style"],
    "harry_potter": ["magic_reveal_ravenclaw"],  # 只测1个学院
    "wings": ["angel_wings", "phoenix_wings"],
    "superhero": ["iron_man"],
    "dance": ["apt"],
    "thanksgiving": ["turkey_chasing"],  # 只测1个火鸡模板
    "effects": ["ash_out", "metallic_liquid"],
    # ... 其他类别
}

# 总计约30-40个代表模板，而非全部134个
```

**智能测试策略**:
```python
test_template_sampling.py

class TestTemplateSampling:
    """模板智能采样测试"""
    
    def __init__(self):
        self.cache = TestResultCache()  # 测试结果缓存
        
    def get_templates_to_test(self):
        """确定需要测试的模板"""
        templates = []
        
        # 1. 新增/修改的模板 (优先)
        templates.extend(get_new_or_modified_templates())
        
        # 2. 上次失败的模板 (重测)
        templates.extend(self.cache.get_failed_templates())
        
        # 3. 每类别采样代表
        for category, samples in TEMPLATE_CATEGORIES.items():
            # 跳过已测试的
            for template in samples:
                if not self.cache.is_recently_tested(template):
                    templates.append(template)
        
        return list(set(templates))  # 去重
    
    def test_templates_batch(self, batch_size=10):
        """批量测试模板"""
        templates = self.get_templates_to_test()
        
        results = []
        for i in range(0, len(templates), batch_size):
            batch = templates[i:i+batch_size]
            
            # 串行测试，避免并发费用
            for template in batch:
                result = self.test_single_template(template)
                results.append(result)
                self.cache.save_result(template, result)
                
                # 间隔等待，避免频率限制
                time.sleep(5)
        
        return results
```

**成本优化**:
- 同类模板只测代表 (火鸡模板有多个，只测1个)
- 缓存测试结果，近期测过的不重测
- 失败模板优先重测
- 新增/修改模板优先测试
- 串行执行，避免并发费用

**成本估算**: 
- 全面测试134个模板: ~¥100+
- 智能采样40个模板: ~¥30-40
- 增量测试 (新增+失败): ~¥5-10

**时间**: 
- 全面测试: ~2-3小时
- 智能采样: ~1小时
- 增量测试: ~15分钟

**触发条件**: 每周全面采样，每日增量测试

---

## 三、测试触发策略

### 自动化触发

| 触发条件 | 运行层级 | 估算成本 | 时间 |
|---------|---------|---------|------|
| 每次提交 | Tier 1 | ¥0 | <1min |
| 每日凌晨 | Tier 1+2+3 | ~¥2-3 | ~10min |
| 每周日 | Tier 1+2+3+4 | ~¥10-15 | ~30min |
| 发布前 | Tier 1+2+3+4+5(采样) | ~¥40-50 | ~1.5h |
| 每月 | Tier 1+2+3+4+5(全面) | ~¥100+ | ~3h |

### 手动触发

| 场景 | 运行测试 | 说明 |
|------|---------|------|
| 修改配置 | Tier 1+2 | 验证配置加载 |
| 新增端口 | Tier 1+2+3+4(新增端口) | 验证新端口 |
| 新增模板 | Tier 1+2+3+5(新增模板) | 验证新模板 |
| 问题排查 | 指定端口/模板 | 定向测试 |

---

## 四、成本估算与控制

### 月度成本估算

| 测试类型 | 频率 | 单次成本 | 月成本 |
|---------|------|---------|--------|
| 提交触发 | ~100次/月 | ¥0 | ¥0 |
| 每日测试 | 30次/月 | ¥2 | ¥60 |
| 每周测试 | 4次/月 | ¥10 | ¥40 |
| 发布测试 | 2次/月 | ¥40 | ¥80 |
| 月度全面 | 1次/月 | ¥100 | ¥100 |
| **总计** | - | - | **~¥280/月** |

### 成本控制措施

1. **智能缓存**
   - 测试图片UUID缓存 (永久有效，手动清除)
   - 测试结果缓存 (永久有效，手动标记失效)
   - 配置缓存

2. **失败重试限制**
   ```python
   MAX_RETRY = 2  # 最多重试2次
   ```

3. **并发控制**
   ```python
   MAX_CONCURRENT = 1  # 串行执行
   TEST_INTERVAL = 5   # 5秒间隔
   ```

4. **预算告警**
   ```python
   DAILY_BUDGET = 10    # 每日预算¥10
   WEEKLY_BUDGET = 50  # 每周预算¥50
   ```

---

## 五、测试数据管理

### 测试图片资产

```
tests/fixtures/
├── images/
│   ├── portrait.jpg      # 人像照片 (主测试图)
│   ├── landscape.jpg     # 风景照片
│   ├── product.jpg       # 产品照片
│   └── animal.jpg        # 动物照片
├── uuids.json            # 预上传图片UUID映射
└── cache/
    ├── test_results.json     # 测试结果缓存
    ├── failed_templates.json # 失败记录
    └── cost_tracking.json    # 成本追踪
```

### 预上传测试图片

```python
# scripts/setup_test_assets.py

def setup_test_assets():
    """预上传测试图片，减少重复上传成本"""
    client = create_client()
    
    test_images = {
        "portrait": "tests/fixtures/images/portrait.jpg",
        "landscape": "tests/fixtures/images/landscape.jpg",
        "product": "tests/fixtures/images/product.jpg",
    }
    
    uuids = {}
    for name, path in test_images.items():
        uuid = client.upload_image(path)
        uuids[name] = uuid
        print(f"Uploaded {name}: {uuid}")
    
    # 保存UUID映射
    with open("tests/fixtures/uuids.json", "w") as f:
        json.dump(uuids, f, indent=2)
    
    return uuids

# 运行: python scripts/setup_test_assets.py
```

---

## 六、测试报告生成

### 报告内容

```python
class TestReport:
    """测试报告"""
    
    def generate(self):
        return {
            "summary": {
                "total_tests": 100,
                "passed": 95,
                "failed": 3,
                "skipped": 2,
                "duration": "10:30",
                "cost": "¥2.50"
            },
            "tier_results": {
                "tier1": {"passed": 50, "failed": 0, "cost": "¥0"},
                "tier2": {"passed": 10, "failed": 0, "cost": "¥0.1"},
                "tier3": {"passed": 6, "failed": 0, "cost": "¥2.2"},
                "tier4": {"passed": 15, "failed": 2, "cost": "¥8.5"},
                "tier5": {"passed": 14, "failed": 1, "cost": "¥15"}
            },
            "failed_items": [
                {"tier": 4, "port": "xxx", "error": "..."},
                {"tier": 5, "template": "yyy", "error": "..."}
            ],
            "recommendations": [
                "端口 xxx 连续失败3次，建议检查",
                "模板 yyy 可能是暂时性问题，建议重试"
            ]
        }
```

---

## 七、实施建议

### 阶段1: 立即实施 (本周)
1. ✅ 创建测试图片资产
2. ✅ 预上传测试图片，获取UUID
3. ✅ 实现Tier 1 (静态测试)
4. ✅ 实现Tier 2 (组件测试)
5. ✅ 实现Tier 3 (核心功能冒烟测试)

### 阶段2: 短期实施 (下周)
6. 实现Tier 4 (端口采样测试)
7. 实现Tier 5 (模板智能采样)
8. 集成测试报告生成
9. 设置定时任务

### 阶段3: 中期优化 (月内)
10. 优化采样算法
11. 完善缓存机制
12. 添加成本监控告警

---

## 八、方案确认检查清单

请确认以下事项：

- [ ] **测试层级划分** - 5层架构是否合理
- [ ] **成本估算** - 月成本~¥280是否可接受
- [ ] **采样策略** - 模板分类采样方法是否合适
- [ ] **触发频率** - 日/周/月的测试频率是否合理
- [ ] **测试图片** - 4种类型图片是否足够 (人像/风景/产品/动物)
- [ ] **缓存策略** - 24小时测试结果缓存是否合适
- [ ] **失败重试** - 最多2次重试 + 1小时冷却是否合理

**请确认或修改后，我将开始编写测试代码。**

---

*方案设计: 2026-03-07*

---

## 附录: 缓存管理详细设计

### 持久化缓存管理器

```python
# tests/fixtures/cache_manager.py

class TestCacheManager:
    """
    持久化测试缓存管理器
    
    缓存策略:
    - 测试图片UUID: 永久有效，手动清除
    - 测试结果: 永久有效，手动标记失效
    - 失败记录: 永久保留，优先重测
    """
    
    CACHE_DIR = Path("tests/fixtures/cache")
    
    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.uuids_file = self.CACHE_DIR / "uuids.json"
        self.results_file = self.CACHE_DIR / "test_results.json"
        self.failures_file = self.CACHE_DIR / "failed_items.json"
    
    # ========== 图片UUID缓存 (永久) ==========
    
    def get_image_uuid(self, image_type: str) -> Optional[str]:
        """获取缓存的图片UUID"""
        if not self.uuids_file.exists():
            return None
        with open(self.uuids_file) as f:
            uuids = json.load(f)
        return uuids.get(image_type)
    
    def save_image_uuid(self, image_type: str, uuid: str):
        """保存图片UUID到缓存"""
        uuids = {}
        if self.uuids_file.exists():
            with open(self.uuids_file) as f:
                uuids = json.load(f)
        uuids[image_type] = uuid
        with open(self.uuids_file, 'w') as f:
            json.dump(uuids, f, indent=2)
    
    def clear_image_uuids(self):
        """清除图片UUID缓存 - 需要重新上传"""
        if self.uuids_file.exists():
            self.uuids_file.unlink()
            print("🗑️  图片UUID缓存已清除，下次测试将重新上传")
    
    # ========== 测试结果缓存 (永久，手动失效) ==========
    
    def get_test_result(self, test_key: str) -> Optional[Dict]:
        """获取缓存的测试结果"""
        if not self.results_file.exists():
            return None
        with open(self.results_file) as f:
            results = json.load(f)
        return results.get(test_key)
    
    def save_test_result(self, test_key: str, result: Dict):
        """保存测试结果"""
        results = {}
        if self.results_file.exists():
            with open(self.results_file) as f:
                results = json.load(f)
        results[test_key] = {
            **result,
            "cached_at": datetime.now().isoformat()
        }
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def invalidate_test_result(self, test_key: str):
        """手动标记测试结果失效"""
        if not self.results_file.exists():
            return
        with open(self.results_file) as f:
            results = json.load(f)
        if test_key in results:
            results[test_key]["invalidated"] = True
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"🗑️  测试结果 {test_key} 已标记为失效")
    
    def clear_test_results(self):
        """清除所有测试结果缓存"""
        if self.results_file.exists():
            self.results_file.unlink()
            print("🗑️  测试结果缓存已清除")
    
    # ========== 失败记录缓存 (永久) ==========
    
    def record_failure(self, item_type: str, item_id: str, error: str):
        """记录失败项"""
        failures = {"templates": {}, "ports": {}}
        if self.failures_file.exists():
            with open(self.failures_file) as f:
                failures = json.load(f)
        
        failures[item_type][item_id] = {
            "error": error,
            "failed_at": datetime.now().isoformat(),
            "retry_count": failures.get(item_type, {}).get(item_id, {}).get("retry_count", 0) + 1
        }
        
        with open(self.failures_file, 'w') as f:
            json.dump(failures, f, indent=2)
    
    def get_failed_items(self, item_type: str) -> List[str]:
        """获取失败项列表"""
        if not self.failures_file.exists():
            return []
        with open(self.failures_file) as f:
            failures = json.load(f)
        return list(failures.get(item_type, {}).keys())
    
    def clear_failure_record(self, item_type: str, item_id: str):
        """清除特定失败记录"""
        if not self.failures_file.exists():
            return
        with open(self.failures_file) as f:
            failures = json.load(f)
        if item_id in failures.get(item_type, {}):
            del failures[item_type][item_id]
            with open(self.failures_file, 'w') as f:
                json.dump(failures, f, indent=2)

# 便捷函数
def get_cache_manager() -> TestCacheManager:
    return TestCacheManager()
```

### 缓存管理命令

用户可以通过指令管理缓存：

| 指令 | 功能 | 影响 |
|------|------|------|
| "清除图片UUID缓存" | 删除 uuids.json | 下次测试需重新上传图片 |
| "清除测试结果缓存" | 删除 test_results.json | 所有测试结果需重新测试 |
| "清除失败记录" | 删除 failed_items.json | 失败历史清零 |
| "清除所有缓存" | 删除全部缓存文件 | 完全重置测试状态 |
| "标记xxx测试失效" | 标记特定测试失效 | 该测试下次会重新执行 |

### AI缓存提醒

当缓存可能影响测试准确性时，AI将主动提醒：

```
AI: "检测到模板 ghibli 的缓存结果已保留7天，是否重新测试？"
AI: "配置管理器代码已修改，建议清除相关测试结果缓存"
AI: "新增模板检测，建议进行 Tier 5 采样测试"
```
