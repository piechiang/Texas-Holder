#!/usr/bin/env python3
"""
Quick demo of core improvements to Texas Hold'em calculator
德州扑克计算器核心改进的快速演示
"""

import time
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from texas_holdem_calculator import parse_card_string, TexasHoldemCalculator


def demo_confidence_intervals():
    """Demonstrate confidence interval calculation"""
    print("🎯 Confidence Interval Demo")
    print("=" * 40)
    
    # Import the confidence interval function
    from src.core.monte_carlo import wilson_confidence_interval, simulate_equity
    
    # Demo Wilson confidence intervals
    print("\nWilson Confidence Intervals:")
    test_cases = [
        (450, 1000),   # 45% win rate with 1000 samples
        (850, 1000),   # 85% win rate with 1000 samples
        (4500, 10000), # 45% win rate with 10000 samples
        (8500, 10000)  # 85% win rate with 10000 samples
    ]
    
    for wins, total in test_cases:
        ci_low, ci_high = wilson_confidence_interval(wins, total)
        win_rate = wins / total
        ci_radius = (ci_high - ci_low) / 2
        
        print(f"  {wins:5}/{total:5} = {win_rate:.1%} ±{ci_radius:.1%} [{ci_low:.1%}, {ci_high:.1%}]")
    
    print("\nKey insight: Larger samples → tighter confidence intervals")


def demo_exact_enumeration():
    """Demonstrate exact enumeration vs Monte Carlo"""
    print("\n🎲 Exact Enumeration vs Monte Carlo")
    print("=" * 45)
    
    from src.core.exact_enumeration import ExactEnumerator
    
    # Test scenario: river situation (exact calculation possible)
    hero_str = "As Kh"
    villain_str = "Qs Qc" 
    board_str = "2c 7d 9h Jc 4s"
    
    hero_cards = [parse_card_string(card) for card in hero_str.split()]
    villain_cards = [parse_card_string(card) for card in villain_str.split()]
    board_cards = [parse_card_string(card) for card in board_str.split()]
    
    print(f"Scenario: {hero_str} vs {villain_str}")
    print(f"Board: {board_str}")
    
    # Exact enumeration (all river cards known)
    print("\n⚡ Exact Enumeration:")
    try:
        enumerator = ExactEnumerator()
        start_time = time.time()
        result = enumerator.enumerate_heads_up(hero_cards, villain_cards, board_cards)
        enum_time = (time.time() - start_time) * 1000
        
        print(f"  Win rate: {result.p_hat:.3%} (exact)")
        print(f"  Scenarios evaluated: {result.n:,}")
        print(f"  Time: {enum_time:.1f}ms")
        print(f"  ✅ Zero sampling error")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    # Monte Carlo comparison
    print("\n🎲 Monte Carlo (10,000 simulations):")
    calculator = TexasHoldemCalculator(random_seed=42)
    
    start_time = time.time()
    mc_result = calculator.calculate_win_probability(
        hole_cards=hero_cards,
        community_cards=board_cards,
        num_opponents=1,
        num_simulations=10000
    )
    mc_time = (time.time() - start_time) * 1000
    
    print(f"  Win rate: {mc_result['win_probability']:.3%} (approximate)")
    print(f"  Simulations: 10,000")
    print(f"  Time: {mc_time:.1f}ms")
    print(f"  ⚠️  Has sampling error")


def demo_method_selection_logic():
    """Show the logic for automatic method selection"""
    print("\n🤖 Method Selection Logic")
    print("=" * 35)
    
    from src.core.exact_enumeration import should_use_enumeration
    
    test_scenarios = [
        ("Preflop heads-up", 1, 0),
        ("Flop heads-up", 1, 3), 
        ("Turn heads-up", 1, 4),
        ("River heads-up", 1, 5),
        ("Flop 3-way", 2, 3),
        ("Turn 3-way", 2, 4),
        ("Preflop 5-way", 4, 0),
    ]
    
    print("\nScenario analysis:")
    print(f"{'Scenario':<18} {'Method':<15} {'Reason'}")
    print("-" * 50)
    
    for scenario, opponents, board_cards in test_scenarios:
        use_enum = should_use_enumeration(opponents, board_cards)
        
        if use_enum:
            method = "Enumeration"
            reason = "Small complexity"
        else:
            method = "Monte Carlo"
            if opponents > 2:
                reason = "Too many opponents"
            elif board_cards < 3:
                reason = "Too many unknowns"
            else:
                reason = "High complexity"
        
        print(f"{scenario:<18} {method:<15} {reason}")


def demo_seed_reproducibility():
    """Demonstrate reproducible results with seeds"""
    print("\n🌱 Seed Reproducibility Demo")
    print("=" * 35)
    
    calculator = TexasHoldemCalculator()
    
    # Test scenario
    hero_cards = [parse_card_string('As'), parse_card_string('Kh')]
    board_cards = [parse_card_string('2c'), parse_card_string('7d')]
    
    print("Same scenario with fixed seed (should be identical):")
    
    for run in range(3):
        result = calculator.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=1,
            num_simulations=5000,
            seed=42  # Fixed seed
        )
        print(f"  Run {run+1}: {result['win_probability']:.4f}")
    
    print("\nSame scenario with random seed (should vary):")
    
    for run in range(3):
        result = calculator.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=1,
            num_simulations=5000,
            seed=None  # Random seed
        )
        print(f"  Run {run+1}: {result['win_probability']:.4f}")


def demo_performance_improvements():
    """Show performance improvement techniques"""
    print("\n⚡ Performance Improvement Techniques")
    print("=" * 45)
    
    print("Key optimizations implemented:")
    print("1. 🎯 Automatic method selection")
    print("   - Enumeration for small scenarios (exact results)")
    print("   - Monte Carlo for complex scenarios")
    print("")
    print("2. 📊 Confidence intervals")
    print("   - Wilson score intervals for accuracy")
    print("   - Early stopping when target precision reached")
    print("")
    print("3. 🔄 Vectorized operations")
    print("   - NumPy batch processing (when available)")
    print("   - 10-50x speedup potential")
    print("")
    print("4. 🚀 Optimized hand evaluation")
    print("   - Numba JIT compilation (when available)")
    print("   - Fast lookup tables")
    print("   - Batch evaluation")
    print("")
    print("5. 🌱 Reproducible results")
    print("   - Seed control for testing")
    print("   - Deterministic enumeration")
    print("")
    print("Installation for maximum performance:")
    print("  pip install numpy numba")


if __name__ == "__main__":
    try:
        print("🎰 Texas Hold'em Calculator - Core Improvements Demo")
        print("=" * 60)
        
        demo_confidence_intervals()
        demo_exact_enumeration()
        demo_method_selection_logic()
        demo_seed_reproducibility()
        demo_performance_improvements()
        
        print("\n🎉 Demo completed successfully!")
        print("\nThese improvements provide:")
        print("✅ Higher accuracy (exact enumeration + confidence intervals)")
        print("✅ Better performance (automatic method selection)")
        print("✅ Reproducible results (seed control)")
        print("✅ Clear uncertainty quantification (confidence intervals)")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()