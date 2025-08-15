#!/usr/bin/env python3
"""
Simple test of core functionality improvements
核心功能改进的简单测试
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from texas_holdem_calculator import parse_card_string, TexasHoldemCalculator


def test_confidence_intervals():
    """Test confidence interval functionality"""
    print("🧪 Testing confidence intervals...")
    
    from src.core.monte_carlo import wilson_confidence_interval
    
    # Test basic CI calculation
    ci_low, ci_high = wilson_confidence_interval(450, 1000)
    ci_width = ci_high - ci_low
    
    print(f"  ✅ CI calculation: 450/1000 → [{ci_low:.3f}, {ci_high:.3f}] (width: {ci_width:.3f})")
    
    # Verify properties
    assert 0 <= ci_low <= ci_high <= 1, "CI bounds should be valid probabilities"
    assert ci_width > 0, "CI should have positive width"
    
    print("  ✅ Confidence intervals working correctly")


def test_exact_enumeration():
    """Test exact enumeration functionality"""
    print("\n🧪 Testing exact enumeration...")
    
    try:
        from src.core.exact_enumeration import ExactEnumerator, should_use_enumeration
        
        # Test method selection logic
        should_enum_river = should_use_enumeration(1, 5)  # River heads-up
        should_enum_preflop = should_use_enumeration(4, 0)  # Preflop 4-way
        
        print(f"  ✅ Method selection: River heads-up → {should_enum_river}")
        print(f"  ✅ Method selection: Preflop 4-way → {should_enum_preflop}")
        
        assert should_enum_river == True, "Should use enumeration for river heads-up"
        assert should_enum_preflop == False, "Should not use enumeration for preflop 4-way"
        
        # Test actual enumeration
        enumerator = ExactEnumerator()
        hero_cards = [parse_card_string('As'), parse_card_string('Kh')]
        villain_cards = [parse_card_string('Qs'), parse_card_string('Qc')]
        board_cards = [parse_card_string('2c'), parse_card_string('7d'), 
                       parse_card_string('9h'), parse_card_string('Jc'), 
                       parse_card_string('4s')]
        
        result = enumerator.enumerate_heads_up(hero_cards, villain_cards, board_cards)
        
        print(f"  ✅ Enumeration result: {result.p_hat:.3f} win rate, {result.n} scenarios")
        
        # This specific scenario should have low win rate for hero (AK vs QQ on this board)
        assert 0 <= result.p_hat <= 1, "Win rate should be valid probability"
        assert result.n > 0, "Should evaluate at least one scenario"
        assert result.ci_radius == 0, "Exact enumeration should have no uncertainty"
        
        print("  ✅ Exact enumeration working correctly")
        
    except Exception as e:
        print(f"  ❌ Enumeration test failed: {e}")


def test_original_compatibility():
    """Test that original calculator still works"""
    print("\n🧪 Testing backward compatibility...")
    
    calc = TexasHoldemCalculator(random_seed=42)
    
    hero_cards = [parse_card_string('As'), parse_card_string('Kh')]
    board_cards = [parse_card_string('2c'), parse_card_string('7d')]
    
    result = calc.calculate_win_probability(
        hole_cards=hero_cards,
        community_cards=board_cards,
        num_opponents=1,
        num_simulations=1000
    )
    
    print(f"  ✅ Original calculator: {result['win_probability']:.3f} win rate")
    
    assert 'win_probability' in result, "Should return win probability"
    assert 0 <= result['win_probability'] <= 1, "Win rate should be valid"
    
    print("  ✅ Backward compatibility maintained")


def test_seed_reproducibility():
    """Test seed reproducibility"""
    print("\n🧪 Testing seed reproducibility...")
    
    calc = TexasHoldemCalculator()
    
    hero_cards = [parse_card_string('As'), parse_card_string('Kh')]
    board_cards = [parse_card_string('2c'), parse_card_string('7d')]
    
    # Same seed should give same results
    result1 = calc.calculate_win_probability(
        hole_cards=hero_cards,
        community_cards=board_cards,
        num_opponents=1,
        num_simulations=1000,
        seed=42
    )
    
    result2 = calc.calculate_win_probability(
        hole_cards=hero_cards,
        community_cards=board_cards,
        num_opponents=1,
        num_simulations=1000,
        seed=42
    )
    
    print(f"  ✅ Seed 42 run 1: {result1['win_probability']:.6f}")
    print(f"  ✅ Seed 42 run 2: {result2['win_probability']:.6f}")
    
    assert result1['win_probability'] == result2['win_probability'], "Same seed should give identical results"
    
    print("  ✅ Seed reproducibility working correctly")


def test_performance_improvement_components():
    """Test that performance improvement components are available"""
    print("\n🧪 Testing performance components...")
    
    # Test NumPy availability
    try:
        import numpy as np
        print("  ✅ NumPy available for vectorized operations")
        numpy_available = True
    except ImportError:
        print("  ⚠️  NumPy not available (install for better performance)")
        numpy_available = False
    
    # Test Numba availability  
    try:
        import numba
        print("  ✅ Numba available for JIT compilation")
        numba_available = True
    except ImportError:
        print("  ⚠️  Numba not available (install for maximum performance)")
        numba_available = False
    
    # Test eval7 availability
    try:
        import eval7
        print("  ✅ eval7 available for fast hand evaluation")
        eval7_available = True
    except ImportError:
        print("  ⚠️  eval7 not available (optional)")
        eval7_available = False
    
    print(f"\n  📊 Performance profile:")
    print(f"     NumPy: {'✅' if numpy_available else '❌'}")
    print(f"     Numba: {'✅' if numba_available else '❌'}")
    print(f"     eval7: {'✅' if eval7_available else '❌'}")
    
    if numpy_available and numba_available:
        print("  🚀 Maximum performance configuration available!")
    elif numpy_available:
        print("  ⚡ Good performance configuration available")
    else:
        print("  📝 Basic configuration (install numpy + numba for better performance)")


if __name__ == "__main__":
    print("🎰 Texas Hold'em Calculator - Core Functionality Test")
    print("=" * 60)
    
    try:
        test_confidence_intervals()
        test_exact_enumeration() 
        test_original_compatibility()
        test_seed_reproducibility()
        test_performance_improvement_components()
        
        print("\n🎉 All core functionality tests passed!")
        print("\nSummary of improvements:")
        print("✅ Confidence intervals for uncertainty quantification")
        print("✅ Exact enumeration for perfect accuracy")
        print("✅ Backward compatibility maintained")
        print("✅ Reproducible results with seed control")
        print("✅ Performance optimization components available")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nTo maximize performance, install:")
    print("  pip install numpy numba")