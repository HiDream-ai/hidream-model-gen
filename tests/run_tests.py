#!/usr/bin/env python3
"""
测试运行器主入口
支持按层级运行测试，成本估算，智能推荐
"""
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Optional

# 添加tests到路径
sys.path.insert(0, str(Path(__file__).parent))

from fixtures.cache_manager import get_cache_manager


class TestRunner:
    """
    测试运行器
    
    职责:
    1. 按层级运行测试
    2. 成本估算和提醒
    3. 测试结果汇总
    4. 智能推荐测试层级
    """
    
    TIER_TESTS = {
        1: {
            "file": "test_tier1_unit.py",
            "name": "Tier 1: 静态/单元测试",
            "cost": 0,
            "time": "<1分钟"
        },
        2: {
            "file": "test_tier2_3_integration.py::TestTier2ComponentIntegration",
            "name": "Tier 2: 组件集成测试",
            "cost": 0.1,
            "time": "<2分钟"
        },
        3: {
            "file": "test_tier2_3_integration.py::TestTier3CoreFeaturesSmoke",
            "name": "Tier 3: 核心功能冒烟测试",
            "cost": 2,
            "time": "~5分钟"
        },
        4: {
            "file": "test_tier4_port_sampling.py",
            "name": "Tier 4: 端口采样测试",
            "cost": 8,
            "time": "~15分钟"
        },
        5: {
            "file": "test_tier5_template_sampling.py",
            "name": "Tier 5: 模板采样测试",
            "cost": 25,
            "time": "~1小时"
        }
    }
    
    def __init__(self):
        self.tests_dir = Path(__file__).parent
        self.cache = get_cache_manager()
    
    def run_tier(self, tier: int, verbose: bool = True) -> bool:
        """
        运行指定层级的测试
        
        Args:
            tier: 测试层级 (1-5)
            verbose: 是否显示详细信息
            
        Returns:
            是否成功
        """
        if tier not in self.TIER_TESTS:
            print(f"❌ 无效的测试层级: {tier}")
            return False
        
        config = self.TIER_TESTS[tier]
        
        print(f"\n{'='*60}")
        print(f"🧪 {config['name']}")
        print(f"💰 预估成本: ¥{config['cost']}")
        print(f"⏱️  预估时间: {config['time']}")
        print(f"{'='*60}\n")
        
        # 对于高成本测试，要求确认
        if config['cost'] > 5:
            confirm = input(f"此测试预估成本 ¥{config['cost']}，是否继续? [y/N]: ")
            if confirm.lower() != 'y':
                print("已取消")
                return False
        
        # 运行测试
        test_file = self.tests_dir / config['file']
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v" if verbose else "-q"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.tests_dir)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ 测试运行失败: {e}")
            return False
    
    def run_tiers(self, tiers: List[int]) -> bool:
        """运行多个层级的测试"""
        total_cost = sum(self.TIER_TESTS[t]["cost"] for t in tiers)
        
        print(f"\n📋 测试计划:")
        for tier in tiers:
            config = self.TIER_TESTS[tier]
            print(f"   Tier {tier}: {config['name']} (¥{config['cost']})")
        print(f"\n💰 总预估成本: ¥{total_cost}")
        
        confirm = input("\n是否开始测试? [y/N]: ")
        if confirm.lower() != 'y':
            print("已取消")
            return False
        
        success = True
        for tier in tiers:
            if not self.run_tier(tier):
                success = False
                # 询问是否继续
                cont = input("\n是否继续下一个层级? [y/N]: ")
                if cont.lower() != 'y':
                    break
        
        return success
    
    def recommend_tier(self, changes: str = "") -> int:
        """
        根据代码变更推荐测试层级
        
        Args:
            changes: 变更描述
            
        Returns:
            推荐的测试层级
        """
        changes_lower = changes.lower()
        
        # 分析变更类型
        if any(k in changes_lower for k in ["doc", "readme", "comment"]):
            return 0  # 无需测试
        
        if any(k in changes_lower for k in ["format", "style", "lint"]):
            return 1
        
        if any(k in changes_lower for k in ["test", "mock"]):
            return 1
        
        if any(k in changes_lower for k in ["util", "helper", "type"]):
            return 1
        
        if any(k in changes_lower for k in ["config", "exception", "log"]):
            return 2
        
        if any(k in changes_lower for k in ["client", "api", "call"]):
            return 3
        
        if any(k in changes_lower for k in ["port", "endpoint"]):
            return 4
        
        if any(k in changes_lower for k in ["template", "pipeline"]):
            return 5
        
        if any(k in changes_lower for k in ["refactor", "major", "arch"]):
            return 5
        
        return 3  # 默认推荐Tier 3
    
    def show_status(self):
        """显示测试状态"""
        print("\n📊 测试状态:")
        print("-" * 40)
        
        for tier, config in self.TIER_TESTS.items():
            print(f"\nTier {tier}: {config['name']}")
            print(f"   成本: ¥{config['cost']} | 时间: {config['time']}")
        
        # 缓存状态
        print("\n📦 缓存状态:")
        summary = self.cache.get_cache_summary()
        print(f"   图片UUID: {len(summary['image_uuids'])} 个")
        print(f"   测试结果: {summary['test_results']['valid']} 个有效")
        print(f"   失败记录: {summary['failures']['templates']} 模板, {summary['failures']['ports']} 端口")
    
    def clear_cache_menu(self):
        """缓存清除菜单"""
        print("\n🗑️  缓存清除菜单:")
        print("   1. 清除图片UUID缓存")
        print("   2. 清除测试结果缓存")
        print("   3. 清除失败记录")
        print("   4. 清除所有缓存")
        print("   0. 取消")
        
        choice = input("\n选择: ")
        
        if choice == "1":
            if self.cache.clear_image_uuids():
                print("✅ 图片UUID缓存已清除")
            else:
                print("ℹ️  无图片UUID缓存")
        
        elif choice == "2":
            if self.cache.clear_test_results():
                print("✅ 测试结果缓存已清除")
            else:
                print("ℹ️  无测试结果缓存")
        
        elif choice == "3":
            if self.cache.clear_all_failures():
                print("✅ 失败记录已清除")
            else:
                print("ℹ️  无失败记录")
        
        elif choice == "4":
            self.cache.clear_all_cache()
            print("✅ 所有缓存已清除")
        
        else:
            print("已取消")


def print_usage():
    """打印使用说明"""
    print("""
使用方法:
    python run_tests.py [命令] [参数]

命令:
    tier N          运行指定层级的测试 (1-5)
    tiers 1,2,3     运行多个层级的测试
    status          显示测试状态和缓存情况
    clear           缓存清除菜单
    recommend       获取测试层级推荐

示例:
    python run_tests.py tier 1
    python run_tests.py tiers 1,2,3
    python run_tests.py status
    python run_tests.py clear
    python run_tests.py recommend

或者直接运行:
    pytest tests/test_tier1_unit.py -v
    pytest tests/test_tier2_3_integration.py -v
    pytest tests/test_tier4_port_sampling.py -v
    pytest tests/test_tier5_template_sampling.py -v
""")


def main():
    """主入口"""
    runner = TestRunner()
    
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    if command == "tier" and len(sys.argv) >= 3:
        tier = int(sys.argv[2])
        runner.run_tier(tier)
    
    elif command == "tiers" and len(sys.argv) >= 3:
        tiers = [int(t) for t in sys.argv[2].split(",")]
        runner.run_tiers(tiers)
    
    elif command == "status":
        runner.show_status()
    
    elif command == "clear":
        runner.clear_cache_menu()
    
    elif command == "recommend":
        print("\n💡 测试层级推荐")
        print("描述你的代码变更，我将推荐测试层级。")
        print("例如: '修改了模板配置' / '重构了API客户端' / '添加新端口'\n")
        
        changes = input("变更描述: ")
        tier = runner.recommend_tier(changes)
        
        if tier == 0:
            print("\n✅ 推荐: 无需测试 (文档/格式变更)")
        else:
            config = runner.TIER_TESTS[tier]
            print(f"\n🎯 推荐测试层级: Tier {tier}")
            print(f"   {config['name']}")
            print(f"   成本: ¥{config['cost']} | 时间: {config['time']}")
            print(f"\n运行: python run_tests.py tier {tier}")
    
    else:
        print_usage()


if __name__ == "__main__":
    main()
