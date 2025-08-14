#!/usr/bin/env python3
"""
Benchmark scenarios for Texas Hold'em Calculator - Truth table with 50 typical scenarios
德州扑克计算器基准场景 - 50个典型场景的真值表

This module defines 50 carefully selected poker scenarios with expected win rate ranges
to serve as regression tests and performance benchmarks. These scenarios cover:
- Preflop situations (premium hands, marginal hands, suited connectors)
- Flop draws (flush draws, straight draws, combo draws)
- Turn decisions (strong hands, bluffs, semi-bluffs)
- River spots (value bets, thin value, bluff catchers)
- Multi-way pots and heads-up situations

本模块定义了50个精心挑选的扑克场景和预期胜率范围，作为回归测试和性能基准。
这些场景涵盖：翻牌前、翻牌圈听牌、转牌圈决策、河牌圈价值下注等。
"""

import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional
from texas_holdem_calculator import TexasHoldemCalculator, Card, Rank, Suit, parse_card_string

@dataclass
class BenchmarkScenario:
    """单个基准场景的定义"""
    name: str
    description: str
    hole_cards: List[Card]
    community_cards: List[Card]
    num_opponents: int
    expected_win_rate_min: float  # 预期胜率最小值
    expected_win_rate_max: float  # 预期胜率最大值
    scenario_type: str  # preflop, flop, turn, river
    notes: str = ""

class PokerBenchmarkSuite:
    """德州扑克基准测试套件"""
    
    def __init__(self):
        self.calculator = TexasHoldemCalculator(random_seed=42)
        self.scenarios = self._create_benchmark_scenarios()
    
    def _create_benchmark_scenarios(self) -> List[BenchmarkScenario]:
        """创建50个基准场景"""
        scenarios = []
        
        # === PREFLOP SCENARIOS (翻牌前场景) === 
        # 1-15: 经典翻牌前对局
        
        scenarios.extend([
            BenchmarkScenario(
                name="AA vs Random",
                description="口袋A对阵随机手牌",
                hole_cards=[parse_card_string("As"), parse_card_string("Ah")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.82,
                expected_win_rate_max=0.87,
                scenario_type="preflop",
                notes="最强起手牌"
            ),
            BenchmarkScenario(
                name="KK vs Random", 
                description="口袋K对阵随机手牌",
                hole_cards=[parse_card_string("Ks"), parse_card_string("Kh")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.78,
                expected_win_rate_max=0.84,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="AKs vs Random",
                description="同花AK对阵随机手牌", 
                hole_cards=[parse_card_string("As"), parse_card_string("Ks")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.65,
                expected_win_rate_max=0.70,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="AKo vs Random",
                description="不同花AK对阵随机手牌",
                hole_cards=[parse_card_string("As"), parse_card_string("Kh")], 
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.62,
                expected_win_rate_max=0.68,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="QQ vs Random",
                description="口袋Q对阵随机手牌",
                hole_cards=[parse_card_string("Qs"), parse_card_string("Qh")],
                community_cards=[],
                num_opponents=1, 
                expected_win_rate_min=0.75,
                expected_win_rate_max=0.81,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="JJ vs Random",
                description="口袋J对阵随机手牌",
                hole_cards=[parse_card_string("Js"), parse_card_string("Jh")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.72,
                expected_win_rate_max=0.78,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="AQs vs Random",
                description="同花AQ对阵随机手牌",
                hole_cards=[parse_card_string("As"), parse_card_string("Qs")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.62,
                expected_win_rate_max=0.68,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="TT vs Random",
                description="口袋10对阵随机手牌",
                hole_cards=[parse_card_string("Ts"), parse_card_string("Th")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.68,
                expected_win_rate_max=0.74,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="99 vs Random",
                description="口袋9对阵随机手牌",
                hole_cards=[parse_card_string("9s"), parse_card_string("9h")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.64,
                expected_win_rate_max=0.70,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="88 vs Random",
                description="口袋8对阵随机手牌",
                hole_cards=[parse_card_string("8s"), parse_card_string("8h")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.61,
                expected_win_rate_max=0.67,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="A5s vs Random",
                description="同花A5对阵随机手牌（轮子听牌）",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.57,
                expected_win_rate_max=0.63,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="KJs vs Random",
                description="同花KJ对阵随机手牌",
                hole_cards=[parse_card_string("Ks"), parse_card_string("Js")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.58,
                expected_win_rate_max=0.64,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="77 vs Random",
                description="口袋7对阵随机手牌",
                hole_cards=[parse_card_string("7s"), parse_card_string("7h")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.58,
                expected_win_rate_max=0.64,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="QTs vs Random", 
                description="同花QT对阵随机手牌",
                hole_cards=[parse_card_string("Qs"), parse_card_string("Ts")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.56,
                expected_win_rate_max=0.62,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="22 vs Random",
                description="口袋2对阵随机手牌",
                hole_cards=[parse_card_string("2s"), parse_card_string("2h")],
                community_cards=[],
                num_opponents=1,
                expected_win_rate_min=0.50,
                expected_win_rate_max=0.56,
                scenario_type="preflop"
            ),
        ])
        
        # === FLOP SCENARIOS (翻牌圈场景) ===
        # 16-30: 翻牌圈各种听牌和成牌
        
        scenarios.extend([
            BenchmarkScenario(
                name="Set on Dry Board",
                description="干燥牌面的三条",
                hole_cards=[parse_card_string("8s"), parse_card_string("8h")],
                community_cards=[parse_card_string("8d"), parse_card_string("3c"), parse_card_string("7h")],
                num_opponents=1,
                expected_win_rate_min=0.88,
                expected_win_rate_max=0.94,
                scenario_type="flop",
                notes="几乎不败的手牌"
            ),
            BenchmarkScenario(
                name="Overpair on Low Board",
                description="低牌面的超对",
                hole_cards=[parse_card_string("As"), parse_card_string("Ah")],
                community_cards=[parse_card_string("7d"), parse_card_string("3c"), parse_card_string("2h")],
                num_opponents=1,
                expected_win_rate_min=0.84,
                expected_win_rate_max=0.90,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Top Pair Top Kicker",
                description="顶对顶踢脚",
                hole_cards=[parse_card_string("As"), parse_card_string("Kh")],
                community_cards=[parse_card_string("Ad"), parse_card_string("7c"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.78,
                expected_win_rate_max=0.84,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Nut Flush Draw", 
                description="坚果同花听牌",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7s"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.44,
                expected_win_rate_max=0.50,
                scenario_type="flop",
                notes="9个坚果听牌"
            ),
            BenchmarkScenario(
                name="Open-Ended Straight Draw",
                description="两头顺听牌",
                hole_cards=[parse_card_string("Js"), parse_card_string("Th")],
                community_cards=[parse_card_string("9d"), parse_card_string("8c"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.32,
                expected_win_rate_max=0.38,
                scenario_type="flop",
                notes="8个听牌"
            ),
            BenchmarkScenario(
                name="Combo Draw",
                description="同花+顺子复合听牌",
                hole_cards=[parse_card_string("8s"), parse_card_string("7s")],
                community_cards=[parse_card_string("9s"), parse_card_string("6h"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.52,
                expected_win_rate_max=0.58,
                scenario_type="flop",
                notes="15个听牌"
            ),
            BenchmarkScenario(
                name="Gutshot",
                description="内顺听牌",
                hole_cards=[parse_card_string("Js"), parse_card_string("Th")],
                community_cards=[parse_card_string("Qd"), parse_card_string("8c"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.18,
                expected_win_rate_max=0.24,
                scenario_type="flop",
                notes="4个听牌"
            ),
            BenchmarkScenario(
                name="Second Pair",
                description="第二对",
                hole_cards=[parse_card_string("Js"), parse_card_string("Th")],
                community_cards=[parse_card_string("Qd"), parse_card_string("Jc"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.24,
                expected_win_rate_max=0.30,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Backdoor Flush Draw",
                description="后门同花听牌",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7h"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.32,
                expected_win_rate_max=0.38,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Weak Pair",
                description="弱对子",
                hole_cards=[parse_card_string("5s"), parse_card_string("5h")],
                community_cards=[parse_card_string("Kd"), parse_card_string("Qc"), parse_card_string("Jh")],
                num_opponents=1,
                expected_win_rate_min=0.12,
                expected_win_rate_max=0.18,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Two Overcards",
                description="两个超牌",
                hole_cards=[parse_card_string("As"), parse_card_string("Kh")],
                community_cards=[parse_card_string("7d"), parse_card_string("6c"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.28,
                expected_win_rate_max=0.34,
                scenario_type="flop",
                notes="6个听牌"
            ),
            BenchmarkScenario(
                name="Flush on Paired Board",
                description="对子牌面的同花",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7s"), parse_card_string("7h")],
                num_opponents=1,
                expected_win_rate_min=0.66,
                expected_win_rate_max=0.72,
                scenario_type="flop",
                notes="担心葫芦"
            ),
            BenchmarkScenario(
                name="Two Pair vs Set Draw",
                description="两对面对三条听牌",
                hole_cards=[parse_card_string("Ks"), parse_card_string("7h")],
                community_cards=[parse_card_string("Kd"), parse_card_string("7c"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.76,
                expected_win_rate_max=0.82,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Straight on Wet Board",
                description="湿润牌面的顺子",
                hole_cards=[parse_card_string("Ts"), parse_card_string("9h")],
                community_cards=[parse_card_string("Jd"), parse_card_string("8c"), parse_card_string("7s")],
                num_opponents=1,
                expected_win_rate_min=0.58,
                expected_win_rate_max=0.64,
                scenario_type="flop",
                notes="担心同花和更大顺子"
            ),
            BenchmarkScenario(
                name="Weak Flush Draw",
                description="弱同花听牌",
                hole_cards=[parse_card_string("7s"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("Js"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.30,
                expected_win_rate_max=0.36,
                scenario_type="flop",
                notes="可能被反超"
            ),
        ])
        
        # === TURN SCENARIOS (转牌圈场景) ===
        # 31-40: 转牌圈决策点
        
        scenarios.extend([
            BenchmarkScenario(
                name="Nut Flush on Turn",
                description="转牌圈坚果同花",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7s"), parse_card_string("3h"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.93,
                expected_win_rate_max=0.97,
                scenario_type="turn",
                notes="几乎坚果"
            ),
            BenchmarkScenario(
                name="Flush Draw on Turn",
                description="转牌圈同花听牌",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7s"), parse_card_string("3h"), parse_card_string("2d")],
                num_opponents=1,
                expected_win_rate_min=0.19,
                expected_win_rate_max=0.25,
                scenario_type="turn",
                notes="9个出牌"
            ),
            BenchmarkScenario(
                name="Open-Ended on Turn",
                description="转牌圈两头顺听牌",
                hole_cards=[parse_card_string("Js"), parse_card_string("Th")],
                community_cards=[parse_card_string("9d"), parse_card_string("8c"), parse_card_string("3h"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.17,
                expected_win_rate_max=0.23,
                scenario_type="turn",
                notes="8个出牌"
            ),
            BenchmarkScenario(
                name="Set vs Flush Draw",
                description="三条对抗同花听牌",
                hole_cards=[parse_card_string("8s"), parse_card_string("8h")],
                community_cards=[parse_card_string("8d"), parse_card_string("7s"), parse_card_string("6s"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.63,
                expected_win_rate_max=0.69,
                scenario_type="turn",
                notes="对手可能有同花"
            ),
            BenchmarkScenario(
                name="Top Two Pair",
                description="顶部两对",
                hole_cards=[parse_card_string("As"), parse_card_string("Kh")],
                community_cards=[parse_card_string("Ad"), parse_card_string("Kc"), parse_card_string("7h"), parse_card_string("3s")],
                num_opponents=1,
                expected_win_rate_min=0.86,
                expected_win_rate_max=0.92,
                scenario_type="turn"
            ),
            BenchmarkScenario(
                name="Bottom Set vs Straight",
                description="小三条对抗顺子听牌",
                hole_cards=[parse_card_string("3s"), parse_card_string("3h")],
                community_cards=[parse_card_string("3d"), parse_card_string("5c"), parse_card_string("6h"), parse_card_string("7s")],
                num_opponents=1,
                expected_win_rate_min=0.70,
                expected_win_rate_max=0.76,
                scenario_type="turn"
            ),
            BenchmarkScenario(
                name="Overpair vs Draw Heavy",
                description="超对面对多听牌牌面",
                hole_cards=[parse_card_string("As"), parse_card_string("Ah")],
                community_cards=[parse_card_string("9s"), parse_card_string("8s"), parse_card_string("7h"), parse_card_string("6c")],
                num_opponents=1,
                expected_win_rate_min=0.44,
                expected_win_rate_max=0.50,
                scenario_type="turn",
                notes="危险牌面"
            ),
            BenchmarkScenario(
                name="Weak Two Pair",
                description="弱两对",
                hole_cards=[parse_card_string("9s"), parse_card_string("6h")],
                community_cards=[parse_card_string("9d"), parse_card_string("6c"), parse_card_string("Kh"), parse_card_string("As")],
                num_opponents=1,
                expected_win_rate_min=0.42,
                expected_win_rate_max=0.48,
                scenario_type="turn"
            ),
            BenchmarkScenario(
                name="Gutshot + Overcard",
                description="内顺听牌+超牌",
                hole_cards=[parse_card_string("As"), parse_card_string("5h")],
                community_cards=[parse_card_string("7d"), parse_card_string("6c"), parse_card_string("4h"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.20,
                expected_win_rate_max=0.26,
                scenario_type="turn",
                notes="7个出牌"
            ),
            BenchmarkScenario(
                name="Middle Pair Turn",
                description="转牌圈中对",
                hole_cards=[parse_card_string("8s"), parse_card_string("8h")],
                community_cards=[parse_card_string("Kd"), parse_card_string("Jc"), parse_card_string("8d"), parse_card_string("3h")],
                num_opponents=1,
                expected_win_rate_min=0.72,
                expected_win_rate_max=0.78,
                scenario_type="turn"
            ),
        ])
        
        # === RIVER SCENARIOS (河牌圈场景) ===
        # 41-45: 河牌圈价值下注和抓诈唬
        
        scenarios.extend([
            BenchmarkScenario(
                name="Nut Flush River",
                description="河牌圈坚果同花",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7s"), parse_card_string("3h"), parse_card_string("2s"), parse_card_string("Jd")],
                num_opponents=1,
                expected_win_rate_min=0.95,
                expected_win_rate_max=1.0,
                scenario_type="river",
                notes="几乎坚果"
            ),
            BenchmarkScenario(
                name="Top Pair River",
                description="河牌圈顶对",
                hole_cards=[parse_card_string("As"), parse_card_string("Kh")],
                community_cards=[parse_card_string("Ad"), parse_card_string("7c"), parse_card_string("3h"), parse_card_string("2s"), parse_card_string("9d")],
                num_opponents=1,
                expected_win_rate_min=0.78,
                expected_win_rate_max=0.88,
                scenario_type="river"
            ),
            BenchmarkScenario(
                name="Straight on Wet River",
                description="湿润河牌面的顺子",
                hole_cards=[parse_card_string("Ts"), parse_card_string("9h")],
                community_cards=[parse_card_string("Jd"), parse_card_string("8c"), parse_card_string("7s"), parse_card_string("3h"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.58,
                expected_win_rate_max=0.68,
                scenario_type="river"
            ),
            BenchmarkScenario(
                name="Bluff Catcher",
                description="抓诈唬牌力",
                hole_cards=[parse_card_string("9s"), parse_card_string("9h")],
                community_cards=[parse_card_string("As"), parse_card_string("Ks"), parse_card_string("Qs"), parse_card_string("Jh"), parse_card_string("2d")],
                num_opponents=1,
                expected_win_rate_min=0.15,
                expected_win_rate_max=0.25,
                scenario_type="river",
                notes="很多牌击败我们"
            ),
            BenchmarkScenario(
                name="River Two Pair",
                description="河牌圈两对",
                hole_cards=[parse_card_string("Ks"), parse_card_string("7h")],
                community_cards=[parse_card_string("Kd"), parse_card_string("7c"), parse_card_string("3h"), parse_card_string("As"), parse_card_string("2s")],
                num_opponents=1,
                expected_win_rate_min=0.72,
                expected_win_rate_max=0.82,
                scenario_type="river"
            ),
        ])
        
        # === MULTI-WAY SCENARIOS (多人底池场景) ===
        # 46-50: 多人底池的复杂情况
        
        scenarios.extend([
            BenchmarkScenario(
                name="AA vs 2 Opponents",
                description="AA单挑两个对手",
                hole_cards=[parse_card_string("As"), parse_card_string("Ah")],
                community_cards=[],
                num_opponents=2,
                expected_win_rate_min=0.68,
                expected_win_rate_max=0.76,
                scenario_type="preflop",
                notes="多人底池胜率下降"
            ),
            BenchmarkScenario(
                name="KK vs 3 Opponents",
                description="KK单挑三个对手",
                hole_cards=[parse_card_string("Ks"), parse_card_string("Kh")],
                community_cards=[],
                num_opponents=3,
                expected_win_rate_min=0.56,
                expected_win_rate_max=0.64,
                scenario_type="preflop"
            ),
            BenchmarkScenario(
                name="Set vs 2 Opponents Flop",
                description="翻牌圈三条对阵两人",
                hole_cards=[parse_card_string("8s"), parse_card_string("8h")],
                community_cards=[parse_card_string("8d"), parse_card_string("7c"), parse_card_string("6s")],
                num_opponents=2,
                expected_win_rate_min=0.78,
                expected_win_rate_max=0.86,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Top Pair vs 2 Opponents",
                description="顶对单挑两个对手",
                hole_cards=[parse_card_string("As"), parse_card_string("Kh")],
                community_cards=[parse_card_string("Ad"), parse_card_string("7c"), parse_card_string("3h")],
                num_opponents=2,
                expected_win_rate_min=0.58,
                expected_win_rate_max=0.66,
                scenario_type="flop"
            ),
            BenchmarkScenario(
                name="Flush Draw vs 3 Opponents",
                description="同花听牌对阵三人",
                hole_cards=[parse_card_string("As"), parse_card_string("5s")],
                community_cards=[parse_card_string("Ks"), parse_card_string("7s"), parse_card_string("3h")],
                num_opponents=3,
                expected_win_rate_min=0.28,
                expected_win_rate_max=0.36,
                scenario_type="flop",
                notes="多人降低听牌价值"
            ),
        ])
        
        return scenarios
    
    def run_benchmark_suite(self, num_simulations: int = 10000, tolerance: float = 0.03) -> bool:
        """
        运行完整的基准测试套件
        
        Args:
            num_simulations: 每个场景的模拟次数
            tolerance: 允许的胜率偏差容忍度
            
        Returns:
            bool: 是否所有场景都通过测试
        """
        print("🎯 Running 50-Scenario Benchmark Suite")
        print("运行50场景基准测试套件")
        print("=" * 80)
        
        passed_scenarios = 0
        failed_scenarios = []
        
        for i, scenario in enumerate(self.scenarios, 1):
            print(f"\n[{i:2d}/50] {scenario.name} ({scenario.scenario_type})")
            print(f"        {scenario.description}")
            
            # 计算实际胜率
            try:
                result = self.calculator.calculate_win_probability(
                    hole_cards=scenario.hole_cards,
                    community_cards=scenario.community_cards,
                    num_opponents=scenario.num_opponents,
                    num_simulations=num_simulations,
                    seed=42  # 确保可重现
                )
                
                actual_win_rate = result['win_probability']
                expected_min = scenario.expected_win_rate_min
                expected_max = scenario.expected_win_rate_max
                
                # 检查是否在预期范围内（加上容忍度）
                in_range = (expected_min - tolerance) <= actual_win_rate <= (expected_max + tolerance)
                
                if in_range:
                    status = "✅ PASS"
                    passed_scenarios += 1
                else:
                    status = "❌ FAIL"
                    failed_scenarios.append({
                        'name': scenario.name,
                        'expected': f"{expected_min:.1%}-{expected_max:.1%}",
                        'actual': f"{actual_win_rate:.1%}",
                        'diff': actual_win_rate - (expected_min + expected_max) / 2
                    })
                
                print(f"        Expected: {expected_min:.1%}-{expected_max:.1%}, Actual: {actual_win_rate:.1%} {status}")
                
                if scenario.notes:
                    print(f"        Notes: {scenario.notes}")
                    
            except Exception as e:
                print(f"        ❌ ERROR: {e}")
                failed_scenarios.append({
                    'name': scenario.name,
                    'expected': f"{scenario.expected_win_rate_min:.1%}-{scenario.expected_win_rate_max:.1%}",
                    'actual': f"ERROR: {e}",
                    'diff': None
                })
        
        # 总结报告
        print("\n" + "=" * 80)
        print("📋 BENCHMARK SUMMARY / 基准测试总结")
        print("-" * 80)
        
        success_rate = passed_scenarios / len(self.scenarios)
        print(f"Overall Success Rate: {passed_scenarios}/{len(self.scenarios)} ({success_rate:.1%})")
        print(f"整体成功率: {passed_scenarios}/{len(self.scenarios)} ({success_rate:.1%})")
        
        if failed_scenarios:
            print(f"\n❌ Failed Scenarios ({len(failed_scenarios)}):")
            print("失败的场景:")
            for failure in failed_scenarios:
                diff_str = f" (diff: {failure['diff']:+.1%})" if failure['diff'] is not None else ""
                print(f"  • {failure['name']}: Expected {failure['expected']}, Got {failure['actual']}{diff_str}")
        
        # 按场景类型统计
        type_stats = {}
        for scenario in self.scenarios:
            scenario_type = scenario.scenario_type
            if scenario_type not in type_stats:
                type_stats[scenario_type] = {'total': 0, 'passed': 0}
            type_stats[scenario_type]['total'] += 1
            
        for failure in failed_scenarios:
            for scenario in self.scenarios:
                if scenario.name == failure['name']:
                    # This one failed, don't increment passed count
                    break
            else:
                # Not found in failures, so it passed
                continue
        
        # Count passes by elimination
        for scenario in self.scenarios:
            scenario_type = scenario.scenario_type
            failed_names = [f['name'] for f in failed_scenarios]
            if scenario.name not in failed_names:
                type_stats[scenario_type]['passed'] += 1
        
        print(f"\n📊 Breakdown by Scenario Type:")
        print("按场景类型分解:")
        for scenario_type, stats in type_stats.items():
            rate = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
            print(f"  • {scenario_type.capitalize()}: {stats['passed']}/{stats['total']} ({rate:.1%})")
        
        return len(failed_scenarios) == 0

def main():
    """运行基准测试套件"""
    benchmark = PokerBenchmarkSuite()
    
    print("🎮 Texas Hold'em Calculator - Benchmark Test Suite")
    print("德州扑克计算器 - 基准测试套件")
    print("\nThis suite tests 50 carefully selected poker scenarios")
    print("against expected win rate ranges to ensure accuracy.")
    print("该套件测试50个精心挑选的扑克场景的预期胜率范围，以确保准确性。")
    
    print(f"\nTotal scenarios loaded: {len(benchmark.scenarios)}")
    print(f"加载的场景总数: {len(benchmark.scenarios)}")
    
    # 运行基准测试
    success = benchmark.run_benchmark_suite(
        num_simulations=5000,  # 平衡精度和速度
        tolerance=0.04  # 4% 容忍度
    )
    
    if success:
        print("\n🎉 All benchmark scenarios passed!")
        print("所有基准场景都通过了！")
        print("\nThis indicates the calculator is producing accurate")
        print("win rate estimates across diverse poker situations.")
        print("这表明计算器在各种扑克情况下都能产生准确的胜率估计。")
    else:
        print("\n⚠️  Some benchmark scenarios failed.")
        print("一些基准场景失败了。")
        print("\nThis might indicate issues with hand evaluation,")
        print("Monte Carlo simulation, or the benchmark expectations.")
        print("这可能表明手牌评估、蒙特卡罗模拟或基准期望存在问题。")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)