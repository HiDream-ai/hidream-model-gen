#!/usr/bin/env python3
"""
智能测试策略优化器
综合考虑历史结果、风险等级、覆盖率、积分成本
实现高性价比测试
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from test_history_manager import get_test_history_manager, FunctionTestRecord


class RiskLevel(Enum):
    """风险等级"""
    CRITICAL = 4  # 从未测试或连续失败
    HIGH = 3      # 超过14天未测试
    MEDIUM = 2    # 超过7天未测试
    LOW = 1       # 最近测试通过
    MINIMAL = 0   # 最近测试通过且稳定


@dataclass
class TestRecommendation:
    """测试推荐项"""
    function_id: str
    function_name: str
    category: str
    credits: int
    risk_level: RiskLevel
    risk_score: float  # 0-100
    priority_score: float  # 综合优先级分数
    days_since_tested: int
    reason: str  # 推荐理由


class SmartTestOptimizer:
    """
    智能测试优化器
    
    优化目标:
    1. 最大化风险覆盖 (优先测试高风险功能)
    2. 最大化新功能覆盖 (优先测试未测试功能)
    3. 最小化积分成本 (优先低成本功能)
    4. 平衡测试稳定性 (避免连续测试同一类别)
    
    策略算法:
    priority_score = (risk_score * 0.4) + (coverage_score * 0.3) + (cost_efficiency * 0.3)
    """
    
    def __init__(self):
        self.history = get_test_history_manager()
    
    def calculate_risk_score(self, func_status: Dict) -> Tuple[float, RiskLevel, str]:
        """
        计算风险分数 (0-100)
        分数越高风险越大
        """
        score = 0
        reasons = []
        
        # 从未测试: 最高风险
        if func_status['total_tests'] == 0:
            score = 100
            reasons.append("从未测试")
            return score, RiskLevel.CRITICAL, "; ".join(reasons)
        
        # 连续失败
        consecutive_failures = func_status.get('consecutive_failures', 0)
        if consecutive_failures >= 3:
            score = 95
            reasons.append(f"连续失败{consecutive_failures}次")
            return score, RiskLevel.CRITICAL, "; ".join(reasons)
        elif consecutive_failures >= 2:
            score += 70
            reasons.append(f"连续失败{consecutive_failures}次")
        elif consecutive_failures >= 1:
            score += 30
            reasons.append("上次失败")
        
        # 未测试天数
        days = func_status.get('days_since_tested')
        if days is not None:
            if days > 30:
                score += 60
                reasons.append(f"超过30天未测试")
            elif days > 14:
                score += 40
                reasons.append(f"超过14天未测试")
            elif days > 7:
                score += 20
                reasons.append(f"超过7天未测试")
            elif days > 3:
                score += 10
                reasons.append(f"超过3天未测试")
        
        # 成功率低
        try:
            pass_rate = float(func_status['pass_rate'].rstrip('%'))
            if pass_rate < 50:
                score += 30
                reasons.append("成功率低于50%")
            elif pass_rate < 80:
                score += 10
                reasons.append("成功率低于80%")
        except:
            pass
        
        # 确定风险等级
        if score >= 80:
            level = RiskLevel.CRITICAL
        elif score >= 60:
            level = RiskLevel.HIGH
        elif score >= 30:
            level = RiskLevel.MEDIUM
        elif score >= 10:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.MINIMAL
        
        return min(score, 100), level, "; ".join(reasons) if reasons else "最近测试正常"
    
    def calculate_cost_efficiency(self, credits: int, risk_score: float) -> float:
        """
        计算成本效率
        风险分数 / 积分成本 = 每积分的风险覆盖
        越高表示性价比越好
        """
        if credits == 0:
            return 0
        # 低成本测试获得更高效率分数
        efficiency = risk_score / credits
        # 额外奖励低成本
        if credits <= 10:
            efficiency *= 1.5
        elif credits <= 30:
            efficiency *= 1.2
        return efficiency
    
    def calculate_coverage_score(self, category: str, tested_funcs: set) -> float:
        """
        计算覆盖率分数
        鼓励测试未覆盖的类别
        """
        all_funcs = self.history.FUNCTIONS
        category_funcs = [f for f, c in all_funcs.items() if c['category'] == category]
        tested_in_category = len([f for f in category_funcs if f in tested_funcs])
        
        if len(category_funcs) == 0:
            return 0
        
        coverage_ratio = tested_in_category / len(category_funcs)
        # 覆盖率越低，分数越高 (鼓励补齐)
        return (1 - coverage_ratio) * 100
    
    def generate_recommendations(
        self,
        budget_credits: int = 100,
        min_risk_level: RiskLevel = RiskLevel.LOW
    ) -> List[TestRecommendation]:
        """
        生成测试推荐列表
        
        Args:
            budget_credits: 积分预算
            min_risk_level: 最低风险等级要求
        """
        recommendations = []
        
        # 获取已测试的功能（用于覆盖率计算）
        tested_funcs = set()
        for func_id, record in self.history._records.items():
            if record.total_tests > 0:
                tested_funcs.add(func_id)
        
        # 计算每个功能的优先级
        for func_id, config in self.history.FUNCTIONS.items():
            status = self.history.get_function_status(func_id)
            
            # 计算风险分数
            risk_score, risk_level, reason = self.calculate_risk_score(status)
            
            # 过滤低优先级
            if risk_level.value < min_risk_level.value:
                continue
            
            # 计算成本效率
            cost_efficiency = self.calculate_cost_efficiency(config['credits'], risk_score)
            
            # 计算覆盖率分数
            coverage_score = self.calculate_coverage_score(config['category'], tested_funcs)
            
            # 综合优先级分数
            # 风险40% + 成本效率30% + 覆盖率30%
            priority_score = (
                risk_score * 0.4 +
                cost_efficiency * 30 * 0.3 +  # 归一化
                coverage_score * 0.3
            )
            
            rec = TestRecommendation(
                function_id=func_id,
                function_name=config['name'],
                category=config['category'],
                credits=config['credits'],
                risk_level=risk_level,
                risk_score=risk_score,
                priority_score=priority_score,
                days_since_tested=status.get('days_since_tested') or 0,
                reason=reason
            )
            recommendations.append(rec)
        
        # 按优先级排序
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        # 按预算筛选
        selected = []
        total_credits = 0
        category_count = {}  # 限制每类别数量，确保多样性
        
        for rec in recommendations:
            # 检查预算
            if total_credits + rec.credits > budget_credits:
                continue
            
            # 检查类别多样性 (每类别最多3个)
            category_count[rec.category] = category_count.get(rec.category, 0) + 1
            if category_count[rec.category] > 3:
                continue
            
            selected.append(rec)
            total_credits += rec.credits
        
        return selected
    
    def generate_tier3_recommendations(self) -> List[TestRecommendation]:
        """生成Tier 3推荐 (核心功能)"""
        # Tier 3 预算: 约100积分，优先图片和基础视频
        return self.generate_recommendations(
            budget_credits=100,
            min_risk_level=RiskLevel.CRITICAL
        )
    
    def generate_tier4_recommendations(self) -> List[TestRecommendation]:
        """生成Tier 4推荐 (端口采样)"""
        # Tier 4 预算: 约80积分，覆盖不同端口
        return self.generate_recommendations(
            budget_credits=80,
            min_risk_level=RiskLevel.HIGH
        )
    
    def generate_tier5_recommendations(self) -> List[TestRecommendation]:
        """生成Tier 5推荐 (模板采样)"""
        # Tier 5 预算: 约150积分，覆盖不同模板
        return self.generate_recommendations(
            budget_credits=150,
            min_risk_level=RiskLevel.MEDIUM
        )
    
    def print_recommendations(self, recommendations: List[TestRecommendation], title: str):
        """打印推荐列表"""
        print('\n' + '='*70)
        print(f'🎯 {title}')
        print('='*70)
        
        if not recommendations:
            print('\n✅ 所有功能都已充分测试，无高风险项')
            return
        
        total_credits = 0
        total_risk_score = 0
        
        for i, rec in enumerate(recommendations, 1):
            risk_emoji = {
                RiskLevel.CRITICAL: '🔴',
                RiskLevel.HIGH: '🟠',
                RiskLevel.MEDIUM: '🟡',
                RiskLevel.LOW: '🟢',
                RiskLevel.MINIMAL: '⚪'
            }.get(rec.risk_level, '⚪')
            
            print(f"\n{i}. {rec.function_name}")
            print(f"   {risk_emoji} 风险等级: {rec.risk_level.name} (分数: {rec.risk_score:.0f})")
            print(f"   💰 积分: {rec.credits} | 优先级: {rec.priority_score:.1f}")
            print(f"   📂 类别: {rec.category}")
            if rec.days_since_tested > 0:
                print(f"   ⏰ 上次测试: {rec.days_since_tested}天前")
            print(f"   📝 原因: {rec.reason}")
            
            total_credits += rec.credits
            total_risk_score += rec.risk_score
        
        print(f"\n{'-'*70}")
        print(f"📊 汇总:")
        print(f"   推荐测试数: {len(recommendations)}")
        print(f"   总积分: {total_credits}")
        print(f"   平均风险分数: {total_risk_score/len(recommendations):.1f}")
        print(f"   风险覆盖: 🔴{sum(1 for r in recommendations if r.risk_level==RiskLevel.CRITICAL)} "
              f"🟠{sum(1 for r in recommendations if r.risk_level==RiskLevel.HIGH)} "
              f"🟡{sum(1 for r in recommendations if r.risk_level==RiskLevel.MEDIUM)}")
        
        print('='*70)


def main():
    """主函数"""
    optimizer = SmartTestOptimizer()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                 智能测试策略优化器                                    ║
║     综合考虑: 风险等级 × 覆盖率 × 积分成本                            ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    # Tier 3 推荐
    tier3 = optimizer.generate_tier3_recommendations()
    optimizer.print_recommendations(tier3, "Tier 3 核心功能推荐 (预算: 100积分)")
    
    # Tier 4 推荐
    print("\n" + "="*70)
    tier4 = optimizer.generate_tier4_recommendations()
    optimizer.print_recommendations(tier4, "Tier 4 端口采样推荐 (预算: 80积分)")
    
    # Tier 5 推荐
    print("\n" + "="*70)
    tier5 = optimizer.generate_tier5_recommendations()
    optimizer.print_recommendations(tier5, "Tier 5 模板采样推荐 (预算: 150积分)")
    
    # 生成优化后的测试计划
    print("\n" + "="*70)
    print("📋 优化后的测试执行建议:")
    print("="*70)
    
    print("""
基于风险分析和成本优化，建议执行顺序:

Phase 1: 紧急风险覆盖 (低成本高回报)
├── 优先测试所有 2-10 积分的从未测试功能
├── 目标: 用最少的积分覆盖最多的风险
└── 预估: 50积分, 覆盖5-6个CRITICAL风险

Phase 2: 核心功能补齐  
├── 测试图片类别的剩余功能
├── 测试视频类别的v3L端口
└── 预估: 80积分

Phase 3: 高价值功能
├── 测试高积分但高风险的功能
└── 预估: 100积分

Phase 4: 模板全面覆盖
├── 按优先级测试模板
└── 预估: 150积分
""")


if __name__ == '__main__':
    main()
