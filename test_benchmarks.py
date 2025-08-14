#!/usr/bin/env python3
"""
Truth Table Benchmarks for Texas Hold'em Calculator
德州扑克计算器基准真值表

This file contains 50 typical poker scenarios with expected win rate ranges
for regression testing and performance validation.

本文件包含50个典型扑克场景及其预期胜率范围，用于回归测试和性能验证。
"""

import time
import json
import sys
from typing import List, Dict, Tuple
from texas_holdem_calculator import TexasHoldemCalculator, Card, Rank, Suit, parse_card_string

class PokerBenchmarks:
    """
    Benchmark suite with 50 typical poker scenarios
    包含50个典型扑克场景的基准测试套件
    """
    
    def __init__(self):
        self.calculator = TexasHoldemCalculator(random_seed=42)
        
        # Define 50 benchmark scenarios with expected win rate ranges vs RANDOM opponents
        # Each scenario: (description, hole_cards, community_cards, opponents, expected_min, expected_max)
        self.scenarios = [
            # Pre-flop scenarios vs random opponents / 翻牌前对随机对手场景
            ("AA vs 1 random opponent preflop", "As Ah", "", 1, 0.80, 0.88),
            ("KK vs 1 random opponent preflop", "Kd Kh", "", 1, 0.78, 0.85),
            ("QQ vs 1 random opponent preflop", "Qs Qc", "", 1, 0.75, 0.82),
            ("JJ vs 1 random opponent preflop", "Js Jd", "", 1, 0.72, 0.79),
            ("TT vs 1 random opponent preflop", "Ts Th", "", 1, 0.68, 0.75),
            ("AK suited vs 1 random opponent preflop", "As Ks", "", 1, 0.62, 0.68),
            ("AK offsuit vs 1 random opponent preflop", "Ad Kh", "", 1, 0.60, 0.66),
            ("AQ suited vs 1 random opponent preflop", "Ac Qc", "", 1, 0.60, 0.67),
            ("AJ suited vs 1 random opponent preflop", "Ah Jh", "", 1, 0.58, 0.65),
            ("AT suited vs 1 random opponent preflop", "As Ts", "", 1, 0.56, 0.63),
            
            # Multi-way preflop / 多人翻牌前
            ("AA vs 2 random opponents preflop", "As Ah", "", 2, 0.68, 0.75),
            ("AA vs 3 random opponents preflop", "As Ah", "", 3, 0.58, 0.65),
            ("KK vs 2 random opponents preflop", "Kd Kh", "", 2, 0.65, 0.72),
            ("QQ vs 2 random opponents preflop", "Qs Qc", "", 2, 0.60, 0.68),
            ("AK suited vs 2 random opponents preflop", "As Ks", "", 2, 0.44, 0.52),
            
            # Weak hands preflop / 弱手牌翻牌前
            ("72 offsuit vs 1 random opponent preflop", "7d 2h", "", 1, 0.30, 0.37),
            ("32 suited vs 1 random opponent preflop", "3s 2s", "", 1, 0.33, 0.40),
            ("T9 suited vs 1 random opponent preflop", "Tc 9c", "", 1, 0.54, 0.62),
            ("65 suited vs 1 random opponent preflop", "6h 5h", "", 1, 0.40, 0.47),
            
            # Flop scenarios with made hands vs random / 翻牌圈成牌对随机对手
            ("Set of aces on A72 rainbow", "As Ah", "Ad 7c 2h", 1, 0.93, 0.99),
            ("Set of kings on K72 rainbow", "Kd Kh", "Ks 7c 2h", 1, 0.93, 0.99),
            ("Overpair on low flop", "As Ah", "Kd 7c 2h", 1, 0.83, 0.90),
            ("Underpair on ace-high flop", "Kd Kh", "Ad 7c 2h", 1, 0.77, 0.85),
            ("Underpair on ace-king flop", "Qs Qc", "Ad Kc 2h", 1, 0.68, 0.76),
            
            # Drawing hands on flop vs random / 翻牌圈听牌对随机对手
            ("Nut flush draw + overcards", "As Ks", "Qd 7s 3s", 1, 0.67, 0.75),
            ("Open-ended straight draw", "Jc Ts", "9h 8d 2c", 1, 0.52, 0.60),
            ("Gutshot straight draw", "Jc Ts", "9h 7d 2c", 1, 0.38, 0.46),
            ("Flush draw + gutshot", "As 7s", "9s 8d 6c", 1, 0.52, 0.60),
            ("Overcards on paired board", "As Kh", "Qd Qc 7h", 1, 0.58, 0.66),
            
            # Turn scenarios vs random / 转牌圈对随机对手  
            ("Set on turn vs random", "7s 7h", "Ad 7c 2h 9d", 1, 0.91, 0.97),
            ("Two pair on turn vs random", "Ad Kh", "Ac Kc 7s 2h", 1, 0.90, 0.96),
            ("Top pair good kicker turn", "Ad Qh", "Ac 7c 2h 9d", 1, 0.82, 0.89),
            ("Flush draw on turn", "As Ks", "Qd 7s 3s Jh", 1, 0.58, 0.66),
            ("Straight draw on turn", "Jc Ts", "9h 8d 2c 4s", 1, 0.42, 0.50),
            
            # River scenarios vs random / 河牌圈对随机对手
            ("Full house on river", "7s 7h", "Ad 7c 2h 9d As", 1, 0.95, 1.00),
            ("Flush on river", "As Ks", "Qd 7s 3s Jh 5s", 1, 0.98, 1.00),
            ("Straight on river", "Jc Ts", "9h 8d 2c 4s 7c", 1, 0.92, 0.98),
            ("Two pair on river", "Ad Kh", "Ac 7c 2h 9d Ks", 1, 0.95, 0.99),
            ("One pair weak on river", "Td 9h", "Tc 7c 2h 9d As", 1, 0.38, 0.46),
            
            # Suited connectors vs random / 同花连张对随机对手
            ("Straight on 965 flop", "8s 7s", "9h 6d 5c", 1, 0.88, 0.95),
            ("Straight on T76 flop", "9c 8c", "Th 7d 6s", 1, 0.90, 0.97),
            ("Straight on 632 flop", "5s 4s", "6h 3d 2c", 1, 0.88, 0.95),
            
            # Small pairs on various flops / 小对子在不同翻牌
            ("Low pair on low flop", "2s 2h", "7d 5c 3h", 1, 0.38, 0.46),
            ("Middle pair on middle flop", "5s 5h", "Jd 8c 4h", 1, 0.52, 0.60),
            ("Underpair on coordinated flop", "8s 8h", "Kd Qc Jh", 1, 0.45, 0.53),
            
            # Performance testing scenarios / 性能测试场景
            ("Premium pair vs random preflop", "Ad Ah", "", 1, 0.80, 0.88),
            ("Strong Broadway vs random preflop", "Kd Qh", "", 1, 0.58, 0.65),
            ("Suited connector vs random preflop", "Ad 5d", "", 1, 0.52, 0.59),
            
            # Edge case scenarios / 边缘场景
            ("Monster draw", "As Ks", "Qd Js Ts", 1, 0.85, 0.93),
            ("Set vs random on dry board", "7s 7h", "7d 2c 5h", 1, 0.90, 0.97),
            ("Two pair vs random on paired board", "Qs Qh", "Qc Jd Jh", 1, 0.85, 0.93),
            ("Nut flush vs random", "As Ks", "Ah 7s 3s 2s", 1, 0.93, 0.99),
            ("Broadway straight vs random", "Jc Ts", "9h 8d 7s Kc", 1, 0.88, 0.95),
        ]
    
    def parse_scenario(self, hole_str: str, community_str: str) -> Tuple[List[Card], List[Card]]:
        """Parse card strings into Card objects"""
        hole_cards = [parse_card_string(card) for card in hole_str.split()] if hole_str else []
        community_cards = [parse_card_string(card) for card in community_str.split()] if community_str else []
        return hole_cards, community_cards
    
    def run_benchmark_scenario(self, description: str, hole_str: str, community_str: str, 
                              opponents: int, expected_min: float, expected_max: float, 
                              simulations: int = 10000) -> Dict:
        """Run a single benchmark scenario"""
        try:
            hole_cards, community_cards = self.parse_scenario(hole_str, community_str)
            
            # Time the calculation
            start_time = time.time()
            result = self.calculator.calculate_win_probability(
                hole_cards=hole_cards,
                community_cards=community_cards,
                num_opponents=opponents,
                num_simulations=simulations,
                seed=42  # Deterministic results
            )
            end_time = time.time()
            
            win_rate = result['win_probability']
            calculation_time = end_time - start_time
            
            # Check if result is within expected range
            in_range = expected_min <= win_rate <= expected_max
            
            return {
                'description': description,
                'win_rate': win_rate,
                'expected_range': f"{expected_min:.1%}-{expected_max:.1%}",
                'in_range': in_range,
                'calculation_time': calculation_time,
                'simulations': simulations,
                'details': {
                    'hole_cards': hole_str,
                    'community_cards': community_str,
                    'opponents': opponents,
                    'tie_rate': result['tie_probability'],
                    'lose_rate': result['lose_probability']
                }
            }
        except Exception as e:
            return {
                'description': description,
                'error': str(e),
                'in_range': False,
                'calculation_time': 0,
                'details': {'hole_cards': hole_str, 'community_cards': community_str, 'opponents': opponents}
            }
    
    def run_all_benchmarks(self, simulations: int = 10000) -> Dict:
        """Run all 50 benchmark scenarios"""
        print(f"🎯 Running {len(self.scenarios)} Benchmark Scenarios")
        print(f"运行 {len(self.scenarios)} 个基准测试场景")
        print(f"Simulations per scenario: {simulations:,}")
        print("=" * 80)
        
        results = []
        total_time = 0
        passed = 0
        
        for i, (description, hole_str, community_str, opponents, expected_min, expected_max) in enumerate(self.scenarios, 1):
            print(f"\n{i:2d}. {description}")
            print(f"    Cards: {hole_str} | {community_str if community_str else 'preflop'} vs {opponents} opponent(s)")
            
            result = self.run_benchmark_scenario(
                description, hole_str, community_str, opponents, expected_min, expected_max, simulations
            )
            
            if 'error' in result:
                print(f"    ❌ ERROR: {result['error']}")
            else:
                win_rate = result['win_rate']
                expected_range = result['expected_range']
                in_range = result['in_range']
                calc_time = result['calculation_time']
                
                status = "✅" if in_range else "❌"
                print(f"    {status} Win Rate: {win_rate:.1%} (Expected: {expected_range}) [{calc_time:.3f}s]")
                
                if in_range:
                    passed += 1
                else:
                    print(f"        ⚠️  Outside expected range!")
                
                total_time += calc_time
            
            results.append(result)
        
        # Calculate summary statistics
        successful_results = [r for r in results if 'error' not in r]
        avg_time = total_time / len(successful_results) if successful_results else 0
        total_simulations = len(successful_results) * simulations
        simulations_per_second = total_simulations / total_time if total_time > 0 else 0
        
        summary = {
            'total_scenarios': len(self.scenarios),
            'passed': passed,
            'failed': len(self.scenarios) - passed,
            'success_rate': passed / len(self.scenarios),
            'total_time': total_time,
            'average_time_per_scenario': avg_time,
            'total_simulations': total_simulations,
            'simulations_per_second': simulations_per_second,
            'scenarios': results
        }
        
        return summary
    
    def save_benchmark_results(self, results: Dict, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file"""
        # Make results JSON serializable
        json_results = results.copy()
        json_results['scenarios'] = []
        
        for scenario in results['scenarios']:
            json_scenario = scenario.copy()
            if 'win_rate' in json_scenario and isinstance(json_scenario['win_rate'], float):
                # Round to avoid floating point precision issues in JSON
                json_scenario['win_rate'] = round(json_scenario['win_rate'], 4)
            json_results['scenarios'].append(json_scenario)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to {filename}")

def main():
    """Run benchmark suite and display results"""
    benchmarks = PokerBenchmarks()
    
    print("🚀 Texas Hold'em Calculator Benchmark Suite")
    print("德州扑克计算器基准测试套件") 
    print("=" * 80)
    print("\nThis benchmark suite tests 50 typical poker scenarios to ensure")
    print("calculation accuracy and detect any regressions in win rate estimates.")
    print("此基准测试套件测试50个典型扑克场景，以确保计算准确性")
    print("并检测胜率估算中的任何回归。")
    
    # Run benchmarks
    results = benchmarks.run_all_benchmarks(simulations=10000)
    
    # Display summary
    print("\n" + "=" * 80)
    print("📊 BENCHMARK SUMMARY / 基准测试总结")
    print("-" * 80)
    
    passed = results['passed']
    total = results['total_scenarios']
    success_rate = results['success_rate']
    total_time = results['total_time']
    avg_time = results['average_time_per_scenario']
    sims_per_sec = results['simulations_per_second']
    
    print(f"Scenarios Passed: {passed}/{total} ({success_rate:.1%})")
    print(f"通过场景数: {passed}/{total} ({success_rate:.1%})")
    print(f"Total Runtime: {total_time:.1f} seconds")
    print(f"总运行时间: {total_time:.1f} 秒")
    print(f"Average Time per Scenario: {avg_time:.3f} seconds")
    print(f"每场景平均时间: {avg_time:.3f} 秒") 
    print(f"Simulation Performance: {sims_per_sec:,.0f} simulations/second")
    print(f"模拟性能: {sims_per_sec:,.0f} 次模拟/秒")
    
    # Save results
    benchmarks.save_benchmark_results(results)
    
    # Final status
    if success_rate >= 0.90:  # Allow 10% tolerance for edge cases
        print(f"\n🎉 Benchmark PASSED! {success_rate:.1%} scenarios within expected ranges.")
        print(f"基准测试通过！{success_rate:.1%} 的场景在预期范围内。")
        return True
    else:
        print(f"\n❌ Benchmark FAILED. Only {success_rate:.1%} scenarios within expected ranges.")
        print(f"基准测试失败。只有 {success_rate:.1%} 的场景在预期范围内。")
        print("\nConsider reviewing scenarios that failed or adjusting expected ranges.")
        print("请考虑检查失败的场景或调整预期范围。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)