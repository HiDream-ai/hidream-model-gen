"""
Vivago AI Skill 测试套件

测试层级:
- Tier 1: 单元测试 (Mock, 零成本)
- Tier 2: 组件集成测试 (极低成本)
- Tier 3: 核心功能冒烟测试 (低成本)
- Tier 4: 端口采样测试 (中等成本)
- Tier 5: 模板采样测试 (高成本)

使用:
    python tests/run_tests.py tier 1      # 运行Tier 1
    python tests/run_tests.py tiers 1,2,3 # 运行Tier 1-3
    python tests/run_tests.py status      # 查看状态
    pytest tests/test_tier1_unit.py -v    # 直接运行
"""

__version__ = "1.0.0"
