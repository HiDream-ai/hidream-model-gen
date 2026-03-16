#!/usr/bin/env python3
"""Tier 1 测试报告生成器"""
import sys
import os

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

def run_basic_tests():
    """运行基础导入和初始化测试"""
    results = []
    
    # Test 1: VivagoClient 导入
    try:
        from vivago_client import VivagoClient
        results.append(("VivagoClient 导入", "✅ 通过"))
    except Exception as e:
        results.append(("VivagoClient 导入", f"❌ 失败: {e}"))
        return results
    
    # Test 2: 客户端初始化
    try:
        client = VivagoClient(token="test-token")
        assert client.token == "test-token"
        results.append(("客户端初始化", "✅ 通过"))
    except Exception as e:
        results.append(("客户端初始化", f"❌ 失败: {e}"))
    
    # Test 3: 配置加载
    try:
        config = client._load_ports_config()
        assert "base_url" in config
        assert "categories" in config
        results.append(("配置加载", "✅ 通过"))
    except Exception as e:
        results.append(("配置加载", f"❌ 失败: {e}"))
    
    # Test 4: 超时配置
    try:
        assert hasattr(client, 'DEFAULT_MAX_RETRIES')
        assert client.DEFAULT_MAX_RETRIES == 360  # 30分钟
        assert client.DEFAULT_RETRY_DELAY == 5
        results.append(("超时配置 (30分钟)", "✅ 通过"))
    except Exception as e:
        results.append(("超时配置", f"❌ 失败: {e}"))
    
    # Test 5: TemplateManager
    try:
        from template_manager import TemplateManager
        tm = TemplateManager()
        results.append(("TemplateManager 导入", "✅ 通过"))
    except Exception as e:
        results.append(("TemplateManager 导入", f"❌ 失败: {e}"))
    
    # Test 6: ConfigManager
    try:
        from config_manager import ConfigManager
        cm = ConfigManager()
        results.append(("ConfigManager 导入", "✅ 通过"))
    except Exception as e:
        results.append(("ConfigManager 导入", f"❌ 失败: {e}"))
    
    return results

if __name__ == "__main__":
    print("="*60)
    print("Tier 1 单元测试报告")
    print("="*60)
    print("测试时间: 2026-03-07")
    print("测试类型: Mock-based (零API成本)")
    print("-"*60)
    
    results = run_basic_tests()
    
    passed = sum(1 for _, r in results if "✅" in r)
    total = len(results)
    
    for name, result in results:
        print(f"{name:.<40} {result}")
    
    print("-"*60)
    print(f"结果: {passed}/{total} 通过 ({passed*100//total}%)")
    print("="*60)
    
    if passed == total:
        print("✅ Tier 1 测试通过!")
    else:
        print(f"⚠️  {total - passed} 项需要关注")
