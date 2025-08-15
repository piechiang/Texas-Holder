#!/usr/bin/env python3
"""
Demo of enhanced Texas Hold'em calculator performance improvements
增强版德州扑克计算器性能改进演示

This script demonstrates the performance improvements achieved through:
- Vectorized Monte Carlo simulation
- Exact enumeration for small scenarios  
- Numba-optimized hand evaluation
- Automatic method selection with confidence intervals
"""

import time
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from texas_holdem_calculator import parse_card_string, TexasHoldemCalculator
from src.core.enhanced_calculator import EnhancedTexasHoldemCalculator, CalculatorConfig


def demo_basic_comparison():
    """Compare original vs enhanced calculator on basic scenarios"""
    print("🎰 Enhanced Texas Hold'em Calculator Performance Demo")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Preflop heads-up (AA vs random)',
            'hero': 'As Ah',
            'board': '',
            'opponents': 1,
            'simulations': 10000
        },
        {
            'name': 'Flop heads-up (overpair vs draws)',
            'hero': 'Qs Qc',
            'board': '2s 7h 9c',
            'opponents': 1,
            'simulations': 10000
        },
        {
            'name': 'Turn multiway (set vs draws)',
            'hero': '8s 8h',
            'board': '8c 7d 5h Jc',
            'opponents': 3,
            'simulations': 20000
        }
    ]
    
    # Initialize calculators
    original_calc = TexasHoldemCalculator(use_fast_evaluator=True, random_seed=42)
    
    enhanced_config = CalculatorConfig(
        prefer_enumeration=True,
        prefer_vectorized=True,
        default_simulations=10000,
        target_ci_radius=0.005
    )
    enhanced_calc = EnhancedTexasHoldemCalculator(enhanced_config)
    
    print("\nTesting scenarios with both calculators...")
    print("-" * 60)
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"   Hero: {scenario['hero']}")
        print(f"   Board: {scenario['board'] or 'Preflop'}")
        print(f"   Opponents: {scenario['opponents']}")
        
        # Parse cards
        hero_cards = [parse_card_string(card) for card in scenario['hero'].split()]
        board_cards = [parse_card_string(card) for card in scenario['board'].split()] if scenario['board'] else []
        
        # Test original calculator
        print("\n   🔄 Original Calculator:")
        start_time = time.time()
        
        try:
            original_result = original_calc.calculate_win_probability(
                hole_cards=hero_cards,
                community_cards=board_cards,
                num_opponents=scenario['opponents'],
                num_simulations=scenario['simulations'],
                seed=42
            )
            original_time = (time.time() - start_time) * 1000
            
            print(f"      Win rate: {original_result['win_probability']:.1%}")
            print(f"      Time: {original_time:.1f}ms")
            print(f"      Method: Monte Carlo simulation")
            
        except Exception as e:
            print(f"      Error: {e}")
            original_time = float('inf')
            original_result = None
        
        # Test enhanced calculator
        print("\n   ⚡ Enhanced Calculator:")
        start_time = time.time()
        
        try:
            enhanced_result = enhanced_calc.calculate_win_probability(
                hole_cards=hero_cards,
                community_cards=board_cards,
                num_opponents=scenario['opponents'],
                seed=42
            )
            enhanced_time = (time.time() - start_time) * 1000
            
            print(f"      Win rate: {enhanced_result.win_probability:.1%} ±{enhanced_result.ci_radius:.1%}")
            print(f"      Time: {enhanced_time:.1f}ms")
            print(f"      Method: {enhanced_result.method}")
            print(f"      Simulations: {enhanced_result.simulations:,}")
            
            # Calculate speedup
            if original_time != float('inf') and enhanced_time > 0:
                speedup = original_time / enhanced_time
                print(f"      ⚡ Speedup: {speedup:.1f}x faster")
            
        except Exception as e:
            print(f"      Error: {e}")


def demo_confidence_intervals():
    """Demonstrate confidence interval functionality"""
    print("\n\n📊 Confidence Interval Demo")
    print("=" * 40)
    
    from src.core.enhanced_calculator import calculate_with_confidence_intervals
    
    scenario = {
        'hero': 'As Kh',
        'board': '2c 7d 9h',
        'opponents': 1
    }
    
    print(f"Scenario: {scenario['hero']} vs {scenario['opponents']} opponent")
    print(f"Board: {scenario['board']}")
    
    # Test different target confidence intervals
    ci_targets = [0.01, 0.005, 0.002]  # ±1%, ±0.5%, ±0.2%
    
    for target_ci in ci_targets:
        print(f"\n🎯 Target CI: ±{target_ci:.1%}")
        
        start_time = time.time()
        result = calculate_with_confidence_intervals(
            hole_cards_str=scenario['hero'],
            community_cards_str=scenario['board'],
            num_opponents=scenario['opponents'],
            target_ci=target_ci,
            seed=42
        )
        elapsed_time = (time.time() - start_time) * 1000
        
        ci_low, ci_high = result['confidence_interval']
        actual_ci = (ci_high - ci_low) / 2
        
        print(f"   Win rate: {result['win_probability']:.1%}")
        print(f"   95% CI: [{ci_low:.1%}, {ci_high:.1%}] (±{actual_ci:.1%})")
        print(f"   Simulations: {result['simulations']:,}")
        print(f"   Time: {elapsed_time:.1f}ms")
        print(f"   Method: {result['method']}")
        
        if result['stopped_early']:
            print("   ✅ Early stopping achieved target CI")


def demo_method_selection():
    """Demonstrate automatic method selection"""
    print("\n\n🤖 Automatic Method Selection Demo")
    print("=" * 45)
    
    enhanced_calc = EnhancedTexasHoldemCalculator()
    
    test_cases = [
        {
            'name': 'River heads-up (exact enumeration)',
            'hero': 'As Kh',
            'board': '2c 7d 9h Jc 4s',
            'opponents': 1
        },
        {
            'name': 'Turn heads-up (exact enumeration)',
            'hero': 'Qs Qc',
            'board': '2s 7h 9c Jd',
            'opponents': 1
        },
        {
            'name': 'Flop multiway (vectorized MC)',
            'hero': '8s 8h',
            'board': '2c 7d 9h',
            'opponents': 4
        },
        {
            'name': 'Preflop multiway (vectorized MC)',
            'hero': 'As Kd',
            'board': '',
            'opponents': 5
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        
        hero_cards = [parse_card_string(card) for card in test_case['hero'].split()]
        board_cards = [parse_card_string(card) for card in test_case['board'].split()] if test_case['board'] else []
        
        start_time = time.time()
        result = enhanced_calc.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=test_case['opponents'],
            seed=42
        )
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"   Selected method: {result.method}")
        print(f"   Win rate: {result.win_probability:.1%} ±{result.ci_radius:.1%}")
        print(f"   Calculations: {result.simulations:,}")
        print(f"   Time: {elapsed_time:.1f}ms")
        
        # Show performance rationale
        if 'enumeration' in result.method:
            print("   ✅ Exact result - no sampling error")
        elif 'vectorized' in result.method:
            print("   ⚡ Vectorized simulation - high performance")
        else:
            print("   🔄 Standard simulation - reliable fallback")


def demo_performance_stats():
    """Show performance statistics"""
    print("\n\n📈 Performance Statistics")
    print("=" * 35)
    
    enhanced_calc = EnhancedTexasHoldemCalculator()
    
    # Run several calculations to build stats
    test_scenarios = [
        ('As Kh', '2c 7d 9h', 1),
        ('Qs Qc', '8s 7h 5d Jc', 1),
        ('8s 8h', '', 3),
        ('As Kd', '2c 7h 9s', 2)
    ]
    
    print("Running test calculations...")
    for hero_str, board_str, opponents in test_scenarios:
        hero_cards = [parse_card_string(card) for card in hero_str.split()]
        board_cards = [parse_card_string(card) for card in board_str.split()] if board_str else []
        
        enhanced_calc.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=opponents,
            seed=42
        )
    
    # Show performance statistics
    stats = enhanced_calc.get_performance_stats()
    
    print(f"\nTotal calculations: {stats['total_calculations']}")
    print(f"Average time: {stats['average_time_ms']:.1f}ms")
    print("\nMethod usage:")
    print(f"  Enumeration: {stats['enumeration_used']} ({stats.get('enumeration_percentage', 0):.1f}%)")
    print(f"  Vectorized MC: {stats['vectorized_mc_used']} ({stats.get('vectorized_percentage', 0):.1f}%)")
    print(f"  Standard MC: {stats['standard_mc_used']} ({stats.get('standard_percentage', 0):.1f}%)")
    
    evaluator_info = stats.get('hand_evaluator', {})
    if evaluator_info:
        print(f"\nHand evaluator: {evaluator_info.get('type', 'unknown')}")
        if 'expected_speedup' in evaluator_info:
            print(f"Expected speedup: {evaluator_info['expected_speedup']}")


if __name__ == "__main__":
    try:
        # Run all demos
        demo_basic_comparison()
        demo_confidence_intervals()
        demo_method_selection()
        demo_performance_stats()
        
        print("\n\n🎉 Demo completed successfully!")
        print("\nKey improvements demonstrated:")
        print("✅ Automatic method selection (enumeration vs Monte Carlo)")
        print("✅ Confidence intervals with early stopping")
        print("✅ Vectorized simulations for better performance")
        print("✅ Seed support for reproducible results")
        print("✅ Performance monitoring and statistics")
        
        print("\nTo install dependencies for maximum performance:")
        print("  pip install numpy numba")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()