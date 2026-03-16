#!/usr/bin/env python3
"""快速运行 Tier 1 单元测试"""
import sys
import os

# 添加scripts到路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

try:
    from vivago_client import VivagoClient
    print("✅ VivagoClient 导入成功")
    
    # 测试初始化
    client = VivagoClient(token="test-token")
    assert client.token == "test-token"
    assert client.headers["Authorization"] == "Bearer test-token"
    print("✅ test_initialization 通过")
    
    # 测试配置加载
    config = client._load_ports_config()
    assert "base_url" in config
    assert "categories" in config
    print("✅ test_load_ports_config 通过")
    
    print("\n" + "="*50)
    print("Tier 1 核心测试通过!")
    print("="*50)
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
