#!/usr/bin/env python3
"""
查看测试历史和状态
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from test_history_manager import get_test_history_manager


def print_menu():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    测试历史查询系统                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. 查看完整测试覆盖率报告                                   ║
║  2. 查看风险功能列表 (需要优先测试)                          ║
║  3. 查看推荐测试列表 (按积分预算)                            ║
║  4. 查看特定功能历史                                         ║
║  5. 记录新的测试结果                                         ║
║  q. 退出                                                     ║
╚══════════════════════════════════════════════════════════════╝
""")


def view_full_report(manager):
    manager.print_full_report()


def view_risky_functions(manager):
    print("\n🔴 风险功能列表 (需要优先测试):")
    print("-" * 70)
    
    risky = manager.get_risky_functions()
    for i, func in enumerate(risky, 1):
        days = func.get('days_since_tested')
        if days is None:
            days_str = "从未测试"
        else:
            days_str = f"{days}天前"
        
        print(f"\n{i}. {func['function_name']}")
        print(f"   类别: {func['category']}")
        print(f"   积分: {func['credits_per_test']}")
        print(f"   上次测试: {days_str}")
        print(f"   风险等级: {func['risk_level']}")
        if func['consecutive_failures'] > 0:
            print(f"   ⚠️  连续失败: {func['consecutive_failures']} 次")


def view_recommended_tests(manager):
    print("\n💰 请输入积分预算 (默认100):")
    try:
        budget = input("预算: ").strip()
        max_credits = int(budget) if budget else 100
    except:
        max_credits = 100
    
    recommended = manager.get_recommended_tests(max_credits)
    
    print(f"\n🎯 推荐测试列表 (预算 {max_credits} 积分):")
    print("-" * 70)
    
    total = 0
    for i, func in enumerate(recommended, 1):
        days = func.get('days_since_tested')
        if days is None:
            days_str = "从未测试"
        else:
            days_str = f"{days}天前"
        
        print(f"\n{i}. {func['function_name']} ({func['credits_per_test']}积分)")
        print(f"   类别: {func['category']} | 上次测试: {days_str}")
        total += func['credits_per_test']
    
    print(f"\n   预估总积分: {total}")
    print(f"   剩余预算: {max_credits - total}")


def view_function_history(manager):
    print("\n📝 可用功能列表:")
    for func_id, config in manager.FUNCTIONS.items():
        print(f"   {func_id}: {config['name']}")
    
    func_id = input("\n输入功能ID: ").strip()
    
    status = manager.get_function_status(func_id)
    if 'error' in status:
        print(f"❌ {status['error']}")
        return
    
    print(f"\n📊 {status['function_name']} - 详细状态:")
    print("-" * 70)
    print(f"   功能ID: {status['function_id']}")
    print(f"   类别: {status['category']}")
    print(f"   每次测试积分: {status['credits_per_test']}")
    print(f"   总测试次数: {status['total_tests']}")
    print(f"   通过次数: {status['passed_tests']}")
    print(f"   失败次数: {status['failed_tests']}")
    print(f"   成功率: {status['pass_rate']}")
    print(f"   上次测试: {status['last_tested'] or '从未'}")
    if status['days_since_tested'] is not None:
        print(f"   距今天数: {status['days_since_tested']}天")
    print(f"   上次通过: {status['last_passed'] or '无'}")
    print(f"   风险等级: {status['risk_level']}")


def record_new_test(manager):
    print("\n📝 记录新的测试结果:")
    
    print("\n可用功能:")
    funcs = list(manager.FUNCTIONS.keys())
    for i, func_id in enumerate(funcs, 1):
        print(f"   {i}. {func_id}")
    
    try:
        choice = int(input("\n选择功能编号: "))
        func_id = funcs[choice - 1]
    except:
        print("❌ 无效选择")
        return
    
    print("\n测试结果:")
    print("   1. passed (通过)")
    print("   2. failed (失败)")
    print("   3. skipped (跳过)")
    
    status_map = {'1': 'passed', '2': 'failed', '3': 'skipped'}
    status_choice = input("选择结果: ").strip()
    status = status_map.get(status_choice, 'passed')
    
    try:
        duration = float(input("测试耗时(秒): ").strip() or "0")
    except:
        duration = 0
    
    notes = input("备注(可选): ").strip() or None
    
    # 获取积分
    credits = manager.FUNCTIONS[func_id]['credits']
    
    # 记录
    manager.record_test(func_id, status, credits, duration, notes=notes)
    
    print(f"\n✅ 已记录: {manager.FUNCTIONS[func_id]['name']} - {status}")


def main():
    manager = get_test_history_manager()
    
    while True:
        print_menu()
        choice = input("选择: ").strip().lower()
        
        if choice == '1':
            view_full_report(manager)
        elif choice == '2':
            view_risky_functions(manager)
        elif choice == '3':
            view_recommended_tests(manager)
        elif choice == '4':
            view_function_history(manager)
        elif choice == '5':
            record_new_test(manager)
        elif choice == 'q':
            print("再见!")
            break
        else:
            print("无效选择")
        
        input("\n按回车继续...")


if __name__ == '__main__':
    main()
