#!/usr/bin/env python3
"""
Comprehensive test suite for Texas Hold'em Calculator with all hand types
德州扑克计算器综合测试套件 - 覆盖所有牌型

Tests all 10 poker hand rankings with deterministic examples:
测试所有10种扑克牌型的确定性示例
"""

import sys
from texas_holdem_calculator import (
    TexasHoldemCalculator, FastHandEvaluator, HandEvaluator, Card, Rank, Suit, HandRank, parse_card_string
)

def test_all_hand_types():
    """Test all 10 poker hand types with specific deterministic examples"""
    print("🧪 Testing All Hand Types / 测试所有牌型")
    print("-" * 60)
    
    evaluator = FastHandEvaluator()
    fallback_evaluator = HandEvaluator()
    
    # Test cases: (cards, expected_rank, description)
    test_cases = [
        # 1. Royal Flush / 皇家同花顺
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.JACK, Suit.SPADES),
            Card(Rank.TEN, Suit.SPADES)
        ], HandRank.ROYAL_FLUSH, "Royal Flush in Spades"),
        
        # 2. Straight Flush / 同花顺
        ([
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.SIX, Suit.HEARTS),
            Card(Rank.FIVE, Suit.HEARTS)
        ], HandRank.STRAIGHT_FLUSH, "9-High Straight Flush"),
        
        # 3. Four of a Kind / 四条
        ([
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES)
        ], HandRank.FOUR_OF_A_KIND, "Four Kings"),
        
        # 4. Full House / 葫芦
        ([
            Card(Rank.JACK, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS),
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.TEN, Suit.CLUBS)
        ], HandRank.FULL_HOUSE, "Jacks Full of Tens"),
        
        # 5. Flush / 同花
        ([
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.NINE, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.CLUBS),
            Card(Rank.FOUR, Suit.CLUBS)
        ], HandRank.FLUSH, "Ace-High Flush in Clubs"),
        
        # 6. Straight / 顺子
        ([
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.NINE, Suit.DIAMONDS),
            Card(Rank.EIGHT, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.SPADES),
            Card(Rank.SIX, Suit.HEARTS)
        ], HandRank.STRAIGHT, "Ten-High Straight"),
        
        # 7. Three of a Kind / 三条
        ([
            Card(Rank.EIGHT, Suit.SPADES),
            Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES)
        ], HandRank.THREE_OF_A_KIND, "Trip Eights"),
        
        # 8. Two Pair / 两对
        ([
            Card(Rank.NINE, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.FIVE, Suit.DIAMONDS),
            Card(Rank.FIVE, Suit.CLUBS),
            Card(Rank.ACE, Suit.SPADES)
        ], HandRank.TWO_PAIR, "Nines and Fives"),
        
        # 9. One Pair / 一对
        ([
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS),
            Card(Rank.NINE, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.SPADES)
        ], HandRank.ONE_PAIR, "Pair of Queens"),
        
        # 10. High Card / 高牌
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.NINE, Suit.DIAMONDS),
            Card(Rank.SEVEN, Suit.CLUBS),
            Card(Rank.FOUR, Suit.SPADES)
        ], HandRank.HIGH_CARD, "Ace High"),
        
        # Additional test cases for edge scenarios / 边缘情况附加测试
        
        # Royal Flush in different suits / 不同花色的皇家同花顺
        ([
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS)
        ], HandRank.ROYAL_FLUSH, "Royal Flush in Hearts"),
        
        # Low Straight Flush (Wheel) / 最小同花顺
        ([
            Card(Rank.FIVE, Suit.DIAMONDS),
            Card(Rank.FOUR, Suit.DIAMONDS),
            Card(Rank.THREE, Suit.DIAMONDS),
            Card(Rank.TWO, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ], HandRank.STRAIGHT_FLUSH, "5-High Straight Flush (Steel Wheel)"),
        
        # Four Aces / 四个A
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.TWO, Suit.SPADES)
        ], HandRank.FOUR_OF_A_KIND, "Four Aces"),
        
        # Full House - Aces full of Deuces / 葫芦 - A满2
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.TWO, Suit.SPADES),
            Card(Rank.TWO, Suit.CLUBS)
        ], HandRank.FULL_HOUSE, "Aces Full of Twos"),
        
        # King-High Flush / K高同花
        ([
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.JACK, Suit.SPADES),
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.EIGHT, Suit.SPADES),
            Card(Rank.THREE, Suit.SPADES)
        ], HandRank.FLUSH, "King-High Flush in Spades"),
        
        # Broadway Straight (A-K-Q-J-10) / 百老汇顺子
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.CLUBS),
            Card(Rank.TEN, Suit.SPADES)
        ], HandRank.STRAIGHT, "Broadway Straight"),
        
        # Trip Aces / 三个A
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.TWO, Suit.CLUBS),
            Card(Rank.THREE, Suit.SPADES)
        ], HandRank.THREE_OF_A_KIND, "Trip Aces"),
        
        # Aces and Kings (Top Two Pair) / 两对 - A和K
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES)
        ], HandRank.TWO_PAIR, "Aces and Kings"),
        
        # Pocket Aces / 口袋A
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.JACK, Suit.SPADES)
        ], HandRank.ONE_PAIR, "Pocket Aces"),
        
        # King High with good kickers / K高牌好踢脚
        ([
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS),
            Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.EIGHT, Suit.SPADES)
        ], HandRank.HIGH_CARD, "King High")
    ]
    
    # Test each hand type with both evaluators
    all_passed = True
    for i, (cards, expected_rank, description) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Testing {description}")
        
        # Test with FastHandEvaluator (eval7 + fallback)
        try:
            rank_fast, values_fast = evaluator.evaluate_hand(cards)
            fast_success = rank_fast == expected_rank
            status_fast = "✅" if fast_success else "❌"
            print(f"    FastEvaluator: {status_fast} {rank_fast.name} (expected: {expected_rank.name})")
            if not fast_success:
                all_passed = False
        except Exception as e:
            print(f"    FastEvaluator: ❌ Error: {e}")
            all_passed = False
        
        # Test with fallback HandEvaluator  
        try:
            rank_fallback, values_fallback = fallback_evaluator.evaluate_hand(cards)
            fallback_success = rank_fallback == expected_rank
            status_fallback = "✅" if fallback_success else "❌"
            print(f"    FallbackEval:  {status_fallback} {rank_fallback.name} (expected: {expected_rank.name})")
            if not fallback_success:
                all_passed = False
        except Exception as e:
            print(f"    FallbackEval:  ❌ Error: {e}")
            all_passed = False
        
        # Display cards for reference
        card_strs = [str(card) for card in cards]
        print(f"    Cards: {', '.join(card_strs)}")
    
    return all_passed

def test_hand_comparisons():
    """Test comparative hand strength with deterministic pairs"""
    print("\n\n🧪 Testing Hand Comparisons / 测试手牌比较")
    print("-" * 60)
    
    evaluator = FastHandEvaluator()
    
    # Test pairs: (stronger_hand, weaker_hand, description)
    comparison_tests = [
        # Royal Flush > Straight Flush
        ([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.SPADES), Card(Rank.JACK, Suit.SPADES), Card(Rank.TEN, Suit.SPADES)
        ], [
            Card(Rank.NINE, Suit.HEARTS), Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS), Card(Rank.SIX, Suit.HEARTS), Card(Rank.FIVE, Suit.HEARTS)
        ], "Royal Flush vs Straight Flush"),
        
        # Four of a Kind > Full House
        ([
            Card(Rank.QUEEN, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.CLUBS), Card(Rank.SEVEN, Suit.SPADES)
        ], [
            Card(Rank.KING, Suit.SPADES), Card(Rank.KING, Suit.HEARTS), Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.CLUBS)
        ], "Four Queens vs Kings Full of Aces"),
        
        # Aces Full > Kings Full
        ([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS), Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.KING, Suit.SPADES), Card(Rank.KING, Suit.CLUBS)
        ], [
            Card(Rank.KING, Suit.HEARTS), Card(Rank.KING, Suit.DIAMONDS), Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS)
        ], "Aces Full of Kings vs Kings Full of Queens"),
        
        # Ace-High Flush > King-High Flush
        ([
            Card(Rank.ACE, Suit.HEARTS), Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.HEARTS), Card(Rank.SIX, Suit.HEARTS), Card(Rank.FOUR, Suit.HEARTS)
        ], [
            Card(Rank.KING, Suit.CLUBS), Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.EIGHT, Suit.CLUBS), Card(Rank.SIX, Suit.CLUBS), Card(Rank.FOUR, Suit.CLUBS)
        ], "Ace-High Flush vs King-High Flush"),
    ]
    
    all_passed = True
    for i, (stronger_cards, weaker_cards, description) in enumerate(comparison_tests, 1):
        print(f"\n{i}. Testing {description}")
        
        try:
            comparison_result = evaluator.compare_hands(stronger_cards, weaker_cards)
            expected_result = 1  # stronger hand should win
            
            success = comparison_result == expected_result
            status = "✅" if success else "❌"
            result_text = "Stronger wins" if comparison_result == 1 else "Weaker wins" if comparison_result == -1 else "Tie"
            
            print(f"    Result: {status} {result_text} (comparison: {comparison_result})")
            
            if not success:
                all_passed = False
                print(f"    Expected stronger hand to win (return 1), got {comparison_result}")
        
        except Exception as e:
            print(f"    ❌ Error: {e}")
            all_passed = False
    
    return all_passed

def test_special_cases():
    """Test special cases like wheel straight, ace-low, etc."""
    print("\n\n🧪 Testing Special Cases / 测试特殊情况")
    print("-" * 60)
    
    evaluator = FastHandEvaluator()
    
    special_cases = [
        # Wheel straight (A-2-3-4-5)
        ([
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.TWO, Suit.HEARTS),
            Card(Rank.THREE, Suit.DIAMONDS),
            Card(Rank.FOUR, Suit.CLUBS),
            Card(Rank.FIVE, Suit.SPADES)
        ], HandRank.STRAIGHT, "Wheel Straight (A-2-3-4-5)"),
        
        # Wheel straight flush
        ([
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.TWO, Suit.HEARTS),
            Card(Rank.THREE, Suit.HEARTS),
            Card(Rank.FOUR, Suit.HEARTS),
            Card(Rank.FIVE, Suit.HEARTS)
        ], HandRank.STRAIGHT_FLUSH, "Wheel Straight Flush"),
    ]
    
    all_passed = True
    for i, (cards, expected_rank, description) in enumerate(special_cases, 1):
        print(f"\n{i}. Testing {description}")
        
        try:
            rank, values = evaluator.evaluate_hand(cards)
            success = rank == expected_rank
            status = "✅" if success else "❌"
            print(f"    Result: {status} {rank.name} (expected: {expected_rank.name})")
            
            if not success:
                all_passed = False
                
            card_strs = [str(card) for card in cards]
            print(f"    Cards: {', '.join(card_strs)}")
        
        except Exception as e:
            print(f"    ❌ Error: {e}")
            all_passed = False
    
    return all_passed

def test_reproducible_monte_carlo():
    """Test that Monte Carlo simulations are reproducible with seeds"""
    print("\n\n🧪 Testing Reproducible Monte Carlo / 测试可重现蒙特卡罗")
    print("-" * 60)
    
    # Test with deterministic seed
    calc1 = TexasHoldemCalculator(random_seed=42)
    calc2 = TexasHoldemCalculator(random_seed=42)
    calc3 = TexasHoldemCalculator(random_seed=123)  # Different seed
    
    hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
    
    # Same seed should produce same results
    result1 = calc1.calculate_win_probability(hole_cards, num_simulations=1000, seed=42)
    result2 = calc2.calculate_win_probability(hole_cards, num_simulations=1000, seed=42)
    
    # Different seed should produce different results
    result3 = calc3.calculate_win_probability(hole_cards, num_simulations=1000, seed=123)
    
    # Check reproducibility with same seed
    same_seed_match = (
        result1['win_probability'] == result2['win_probability'] and
        result1['tie_probability'] == result2['tie_probability']
    )
    
    # Check that different seeds produce different results
    different_seed_differ = (
        result1['win_probability'] != result3['win_probability'] or
        result1['tie_probability'] != result3['tie_probability']
    )
    
    print(f"Same seed results match: {'✅' if same_seed_match else '❌'}")
    print(f"  Seed 42 Run 1: Win {result1['win_probability']:.3f}, Tie {result1['tie_probability']:.3f}")
    print(f"  Seed 42 Run 2: Win {result2['win_probability']:.3f}, Tie {result2['tie_probability']:.3f}")
    
    print(f"Different seeds produce different results: {'✅' if different_seed_differ else '❌'}")
    print(f"  Seed 42:  Win {result1['win_probability']:.3f}, Tie {result1['tie_probability']:.3f}")
    print(f"  Seed 123: Win {result3['win_probability']:.3f}, Tie {result3['tie_probability']:.3f}")
    
    return same_seed_match and different_seed_differ

def main():
    """Run comprehensive test suite"""
    print("🚀 Comprehensive Texas Hold'em Calculator Test Suite")
    print("德州扑克计算器综合测试套件")
    print("=" * 80)
    
    test_results = []
    
    # Run all test suites
    test_functions = [
        ("Hand Type Recognition", test_all_hand_types),
        ("Hand Comparisons", test_hand_comparisons),
        ("Special Cases", test_special_cases),
        ("Reproducible Monte Carlo", test_reproducible_monte_carlo)
    ]
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            test_results.append((test_name, result))
            print(f"\n{test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"\n{test_name}: ❌ ERROR - {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY / 测试总结")
    print("-" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    print("整体结果:", f"{passed}/{total} 测试套件通过")
    
    if passed == total:
        print("\n🎉 All tests passed! Calculator is working correctly.")
        print("所有测试通过！计算器工作正常。")
        return True
    else:
        print(f"\n❌ {total - passed} test suite(s) failed. Please review the output above.")
        print(f"有 {total - passed} 个测试套件失败，请查看上面的输出。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)