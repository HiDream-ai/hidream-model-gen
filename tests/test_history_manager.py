#!/usr/bin/env python3
"""
测试历史记录器
追踪每个功能的测试历史、版本迭代、风险识别
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TestHistoryEntry:
    """单次测试记录"""
    timestamp: str
    version: str  # 代码版本 (git commit hash)
    status: str  # 'passed', 'failed', 'skipped'
    credits_used: int
    duration_seconds: float
    error_message: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class FunctionTestRecord:
    """功能测试记录"""
    function_id: str  # 如: 'text_to_image_kling', 'video_img2vid_v3l'
    function_name: str  # 显示名称
    category: str  # 'image', 'video', 'template'
    credits_per_test: int
    
    # 测试历史
    test_history: List[Dict]  # TestHistoryEntry 列表
    
    # 统计
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    
    # 风险标记
    last_tested: Optional[str] = None
    last_passed: Optional[str] = None
    consecutive_failures: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FunctionTestRecord':
        return cls(**data)


class TestHistoryManager:
    """
    测试历史管理器
    
    功能:
    1. 记录每次测试的详细历史
    2. 追踪代码版本迭代
    3. 识别风险功能 (很久未测试或频繁失败)
    4. 推荐优先测试的功能
    5. 生成测试覆盖率报告
    """
    
    HISTORY_FILE = Path(__file__).parent / 'cache' / 'test_history.json'
    
    # 所有可测试的功能定义
    FUNCTIONS = {
        # 图片功能
        'text_to_image_kling': {
            'name': '文生图 (Kling O1)',
            'category': 'image',
            'credits': 8
        },
        'text_to_image_hidream': {
            'name': '文生图 (Vivago 2.0)',
            'category': 'image',
            'credits': 2
        },
        'text_to_image_nano': {
            'name': '文生图 (Nano Banana)',
            'category': 'image',
            'credits': 10
        },
        'image_to_image_kling': {
            'name': '图生图 (Kling O1)',
            'category': 'image',
            'credits': 8
        },
        'image_to_image_nano': {
            'name': '图生图 (Nano Banana)',
            'category': 'image',
            'credits': 10
        },
        
        # 视频功能
        'video_img2vid_v3l': {
            'name': '图生视频 (v3L 360p)',
            'category': 'video',
            'credits': 20
        },
        'video_img2vid_v3pro': {
            'name': '图生视频 (v3Pro)',
            'category': 'video',
            'credits': 30
        },
        'video_img2vid_kling': {
            'name': '图生视频 (Kling video O1)',
            'category': 'video',
            'credits': 80
        },
        'video_txt2vid_v3l': {
            'name': '文生视频 (v3L 360p)',
            'category': 'video',
            'credits': 20
        },
        'video_txt2vid_v3pro': {
            'name': '文生视频 (v3Pro)',
            'category': 'video',
            'credits': 30
        },
        'video_txt2vid_kling': {
            'name': '文生视频 (Kling video O1)',
            'category': 'video',
            'credits': 80
        },
        'video_keyframe_v3l': {
            'name': '视频首尾帧 (v3L)',
            'category': 'video',
            'credits': 20
        },
        'video_keyframe_v3pro': {
            'name': '视频首尾帧 (v3Pro)',
            'category': 'video',
            'credits': 30
        },
        
        # 视频模板
        'template_ghibli': {
            'name': '模板: Ghibli',
            'category': 'template',
            'credits': 30
        },
        'template_iron_man': {
            'name': '模板: Iron Man',
            'category': 'template',
            'credits': 30
        },
        'template_barbie': {
            'name': '模板: Barbie',
            'category': 'template',
            'credits': 30
        },
        'template_angel_wings': {
            'name': '模板: Angel Wings',
            'category': 'template',
            'credits': 30
        },
        'template_renovation': {
            'name': '模板: Renovation of Old Photos',
            'category': 'template',
            'credits': 30
        },
    }
    
    def __init__(self):
        self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._records = self._load_history()
        self._ensure_all_functions()
    
    def _load_history(self) -> Dict[str, FunctionTestRecord]:
        """加载历史记录"""
        if not self.HISTORY_FILE.exists():
            return {}
        
        with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = {}
        for func_id, record_data in data.items():
            records[func_id] = FunctionTestRecord.from_dict(record_data)
        
        return records
    
    def _save_history(self):
        """保存历史记录"""
        data = {func_id: record.to_dict() for func_id, record in self._records.items()}
        with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _ensure_all_functions(self):
        """确保所有功能都有记录"""
        for func_id, config in self.FUNCTIONS.items():
            if func_id not in self._records:
                self._records[func_id] = FunctionTestRecord(
                    function_id=func_id,
                    function_name=config['name'],
                    category=config['category'],
                    credits_per_test=config['credits'],
                    test_history=[]
                )
    
    def get_git_version(self) -> str:
        """获取当前git版本"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except:
            return 'unknown'
    
    def record_test(
        self,
        function_id: str,
        status: str,
        credits_used: int,
        duration_seconds: float,
        error_message: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """记录一次测试"""
        if function_id not in self._records:
            print(f"⚠️  未知功能: {function_id}")
            return
        
        record = self._records[function_id]
        
        # 创建历史条目
        entry = TestHistoryEntry(
            timestamp=datetime.now().isoformat(),
            version=self.get_git_version(),
            status=status,
            credits_used=credits_used,
            duration_seconds=duration_seconds,
            error_message=error_message,
            notes=notes
        )
        
        # 添加到历史
        record.test_history.append(asdict(entry))
        record.total_tests += 1
        
        if status == 'passed':
            record.passed_tests += 1
            record.consecutive_failures = 0
            record.last_passed = entry.timestamp
        elif status == 'failed':
            record.failed_tests += 1
            record.consecutive_failures += 1
        
        record.last_tested = entry.timestamp
        
        # 保存
        self._save_history()
    
    def get_function_status(self, function_id: str) -> Dict:
        """获取功能状态"""
        if function_id not in self._records:
            return {'error': 'Function not found'}
        
        record = self._records[function_id]
        
        # 计算距今天数
        days_since_tested = None
        days_since_passed = None
        
        if record.last_tested:
            last_tested = datetime.fromisoformat(record.last_tested)
            days_since_tested = (datetime.now() - last_tested).days
        
        if record.last_passed:
            last_passed = datetime.fromisoformat(record.last_passed)
            days_since_passed = (datetime.now() - last_passed).days
        
        # 计算成功率
        pass_rate = 0
        if record.total_tests > 0:
            pass_rate = (record.passed_tests / record.total_tests) * 100
        
        return {
            'function_id': function_id,
            'function_name': record.function_name,
            'category': record.category,
            'credits_per_test': record.credits_per_test,
            'total_tests': record.total_tests,
            'passed_tests': record.passed_tests,
            'failed_tests': record.failed_tests,
            'pass_rate': f'{pass_rate:.1f}%',
            'last_tested': record.last_tested,
            'days_since_tested': days_since_tested,
            'last_passed': record.last_passed,
            'days_since_passed': days_since_passed,
            'consecutive_failures': record.consecutive_failures,
            'risk_level': self._calculate_risk_level(record)
        }
    
    def _calculate_risk_level(self, record: FunctionTestRecord) -> str:
        """计算风险等级"""
        # 高风险: 从未测试过
        if record.total_tests == 0:
            return '🔴 HIGH (从未测试)'
        
        # 高风险: 连续失败
        if record.consecutive_failures >= 2:
            return '🔴 HIGH (连续失败)'
        
        # 中风险: 超过7天未测试
        if record.last_tested:
            days = (datetime.now() - datetime.fromisoformat(record.last_tested)).days
            if days > 14:
                return '🟠 MEDIUM (超过14天未测试)'
            if days > 7:
                return '🟡 LOW (超过7天未测试)'
        
        # 低风险: 最近测试通过
        return '🟢 LOW (最近测试正常)'
    
    def get_risky_functions(self, min_days: int = 7) -> List[Dict]:
        """获取风险功能列表"""
        risky = []
        
        for func_id, record in self._records.items():
            status = self.get_function_status(func_id)
            
            # 从未测试
            if record.total_tests == 0:
                risky.append(status)
                continue
            
            # 连续失败
            if record.consecutive_failures >= 2:
                risky.append(status)
                continue
            
            # 超过指定天数未测试
            if status['days_since_tested'] and status['days_since_tested'] > min_days:
                risky.append(status)
        
        # 按风险排序 (从未测试 > 连续失败 > 天数)
        risky.sort(key=lambda x: (
            x['total_tests'] == 0,  # 从未测试排最前
            x['consecutive_failures'] >= 2,  # 然后连续失败
            x['days_since_tested'] or 0  # 然后按天数
        ), reverse=True)
        
        return risky
    
    def get_recommended_tests(self, max_credits: int = 100) -> List[Dict]:
        """获取推荐的测试列表"""
        risky = self.get_risky_functions(min_days=3)
        
        # 优先从未测试的，然后是很久没测试的
        never_tested = [f for f in risky if f['total_tests'] == 0]
        long_time_no_test = [f for f in risky if f['total_tests'] > 0 and f.get('days_since_tested', 0) > 7]
        
        recommended = never_tested + long_time_no_test
        
        # 按积分限制筛选
        selected = []
        total_credits = 0
        
        for func in recommended:
            if total_credits + func['credits_per_test'] <= max_credits:
                selected.append(func)
                total_credits += func['credits_per_test']
        
        return selected
    
    def generate_coverage_report(self) -> Dict:
        """生成测试覆盖率报告"""
        total_functions = len(self.FUNCTIONS)
        tested_functions = sum(1 for r in self._records.values() if r.total_tests > 0)
        passed_functions = sum(1 for r in self._records.values() if r.last_passed is not None)
        
        # 按类别统计
        categories = {}
        for func_id, record in self._records.items():
            cat = record.category
            if cat not in categories:
                categories[cat] = {'total': 0, 'tested': 0, 'passed': 0}
            
            categories[cat]['total'] += 1
            if record.total_tests > 0:
                categories[cat]['tested'] += 1
            if record.last_passed:
                categories[cat]['passed'] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_functions': total_functions,
                'tested_functions': tested_functions,
                'passed_functions': passed_functions,
                'test_coverage': f'{(tested_functions/total_functions*100):.1f}%',
                'pass_coverage': f'{(passed_functions/total_functions*100):.1f}%'
            },
            'by_category': categories,
            'risky_functions': len(self.get_risky_functions()),
            'untested_functions': total_functions - tested_functions
        }
    
    def print_full_report(self):
        """打印完整报告"""
        report = self.generate_coverage_report()
        
        print('\n' + '='*70)
        print('📊 Vivago AI Skill - 测试覆盖率报告')
        print('='*70)
        
        # 总体统计
        print(f"\n📈 总体统计:")
        print(f"   总功能数: {report['summary']['total_functions']}")
        print(f"   已测试: {report['summary']['tested_functions']}")
        print(f"   最近通过: {report['summary']['passed_functions']}")
        print(f"   测试覆盖率: {report['summary']['test_coverage']}")
        print(f"   通过覆盖率: {report['summary']['pass_coverage']}")
        
        # 按类别
        print(f"\n📂 按类别统计:")
        for cat, stats in report['by_category'].items():
            coverage = stats['tested'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"   {cat}: {stats['tested']}/{stats['total']} 已测试 ({coverage:.0f}%)")
        
        # 风险功能
        print(f"\n⚠️  风险功能: {report['risky_functions']} 个")
        
        # 推荐测试
        print(f"\n🎯 推荐优先测试 (100积分预算):")
        recommended = self.get_recommended_tests(max_credits=100)
        total_credits = 0
        for func in recommended[:5]:  # 只显示前5个
            days = func.get('days_since_tested', 'N/A')
            if days == 'N/A' or days is None:
                days_str = '从未测试'
            else:
                days_str = f'{days}天前'
            print(f"   • {func['function_name']} ({func['credits_per_test']}积分) - {days_str}")
            total_credits += func['credits_per_test']
        print(f"   预估总积分: {total_credits}")
        
        print('\n' + '='*70)


# 便捷函数
def get_test_history_manager() -> TestHistoryManager:
    """获取测试历史管理器实例"""
    return TestHistoryManager()


if __name__ == '__main__':
    # 测试历史管理器
    manager = get_test_history_manager()
    
    # 记录本次Tier 3测试结果
    print("正在记录Tier 3测试结果...")
    
    # 图片功能
    manager.record_test('text_to_image_kling', 'passed', 8, 10)
    manager.record_test('image_to_image_kling', 'passed', 8, 15)
    
    # 视频功能
    manager.record_test('video_img2vid_v3l', 'passed', 20, 180)
    manager.record_test('video_txt2vid_v3l', 'passed', 20, 300)
    manager.record_test('video_keyframe_v3l', 'passed', 20, 240)
    manager.record_test('template_ghibli', 'passed', 30, 600)
    
    # 打印报告
    manager.print_full_report()
    
    # 显示风险功能
    print("\n🔴 高风险功能 (需要优先测试):")
    risky = manager.get_risky_functions()
    for func in risky[:10]:
        print(f"   • {func['function_name']} - {func['risk_level']}")
