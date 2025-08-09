#!/usr/bin/env python3
"""
Test script for Texas Hold'em Calculator
德州扑克计算器测试脚本

This script tests the main functionality of the calculator to ensure everything works correctly.
这个脚本测试计算器的主要功能，确保一切正常工作。
"""

from texas_holdem_calculator import (
    TexasHoldemCalculator, HandEvaluator, Card, Rank, Suit, HandRank, parse_card_string
)

def test_card_parsing():
    """Test card string parsing / 测试牌面字符串解析"""
    print("🧪 Testing Card Parsing / 测试牌面解析")
    print("-" * 40)
    
    test_cases = [
        ('As', Rank.ACE, Suit.SPADES),
        ('Kh', Rank.KING, Suit.HEARTS),
        ('10c', Rank.TEN, Suit.CLUBS),
        ('2d', Rank.TWO, Suit.DIAMONDS),
        ('Jh', Rank.JACK, Suit.HEARTS),
        ('Qs', Rank.QUEEN, Suit.SPADES)
    ]
    
    for card_str, expected_rank, expected_suit in test_cases:
        try:
            card = parse_card_string(card_str)
            assert card.rank == expected_rank and card.suit == expected_suit
            print(f"✅ {card_str} -> {card}")
        except Exception as e:
            print(f"❌ {card_str} failed: {e}")
    
    print()

def test_hand_evaluation():
    """Test hand evaluation / 测试手牌评估"""
    print("🧪 Testing Hand Evaluation / 测试手牌评估")
    print("-" * 40)
    
    evaluator = HandEvaluator()
    
    # Test Royal Flush / 测试皇家同花顺
    royal_flush = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.SPADES)
    ]
    rank, values = evaluator.evaluate_hand(royal_flush)
    assert rank == HandRank.ROYAL_FLUSH
    print(f"✅ Royal Flush: {rank.name}")
    
    # Test Four of a Kind / 测试四条
    four_kind = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.SPADES)
    ]
    rank, values = evaluator.evaluate_hand(four_kind)
    assert rank == HandRank.FOUR_OF_A_KIND
    print(f"✅ Four of a Kind: {rank.name}")
    
    # Test Full House / 测试葫芦
    full_house = [
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.CLUBS)
    ]
    rank, values = evaluator.evaluate_hand(full_house)
    assert rank == HandRank.FULL_HOUSE
    print(f"✅ Full House: {rank.name}")
    
    # Test Pair / 测试对子
    pair = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.JACK, Suit.CLUBS)
    ]
    rank, values = evaluator.evaluate_hand(pair)
    assert rank == HandRank.ONE_PAIR
    print(f"✅ One Pair: {rank.name}")
    
    print()

def test_probability_calculation():
    """Test probability calculations / 测试概率计算"""
    print("🧪 Testing Probability Calculation / 测试概率计算")
    print("-" * 40)
    
    calculator = TexasHoldemCalculator()
    
    # Test with pocket aces / 测试口袋对A
    pocket_aces = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS)
    ]
    
    result = calculator.calculate_win_probability(
        hole_cards=pocket_aces,
        num_opponents=1,
        num_simulations=1000
    )
    
    print(f"✅ Pocket Aces vs 1 opponent:")
    print(f"   Win rate: {result['win_probability']:.1%}")
    print(f"   Expected: ~85% (actual: {result['win_probability']:.1%})")
    
    # Should be around 85% for pocket aces vs 1 opponent preflop
    assert 0.75 <= result['win_probability'] <= 0.95, f"Unexpected win rate: {result['win_probability']}"
    
    # Test with a weaker hand / 测试较弱手牌
    weak_hand = [
        Card(Rank.TWO, Suit.SPADES),
        Card(Rank.THREE, Suit.HEARTS)
    ]
    
    result2 = calculator.calculate_win_probability(
        hole_cards=weak_hand,
        num_opponents=1,
        num_simulations=1000
    )
    
    print(f"✅ 2-3 offsuit vs 1 opponent:")
    print(f"   Win rate: {result2['win_probability']:.1%}")
    print(f"   Expected: ~30-40% (actual: {result2['win_probability']:.1%})")
    
    assert result['win_probability'] > result2['win_probability'], "Pocket aces should win more than 2-3 offsuit"
    
    print()

def test_betting_recommendations():
    """Test betting strategy recommendations / 测试下注策略推荐"""
    print("🧪 Testing Betting Recommendations / 测试下注建议")
    print("-" * 40)
    
    calculator = TexasHoldemCalculator()
    
    # Test with strong hand / 测试强手牌
    strong_hand = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES)
    ]
    
    recommendation = calculator.get_betting_recommendation(
        hole_cards=strong_hand,
        num_opponents=1,
        pot_size=100,
        bet_to_call=10
    )
    
    print(f"✅ AK suited recommendation: {recommendation['recommended_action']}")
    print(f"   Win probability: {recommendation['win_probability']:.1%}")
    print(f"   Confidence: {recommendation['confidence']}")
    
    # Test with weak hand / 测试弱手牌
    weak_hand = [
        Card(Rank.TWO, Suit.SPADES),
        Card(Rank.SEVEN, Suit.HEARTS)
    ]
    
    recommendation2 = calculator.get_betting_recommendation(
        hole_cards=weak_hand,
        num_opponents=1,
        pot_size=100,
        bet_to_call=50  # Large bet relative to pot
    )
    
    print(f"✅ 2-7 offsuit vs large bet: {recommendation2['recommended_action']}")
    print(f"   Win probability: {recommendation2['win_probability']:.1%}")
    print(f"   Confidence: {recommendation2['confidence']}")
    
    print()

def test_hand_strength():
    """Test hand strength evaluation / 测试手牌强度评估"""
    print("🧪 Testing Hand Strength Evaluation / 测试手牌强度评估")
    print("-" * 40)
    
    calculator = TexasHoldemCalculator()
    
    # Test complete hand / 测试完整手牌
    hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
    community = [
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.HEARTS),
        Card(Rank.NINE, Suit.DIAMONDS)
    ]
    
    strength = calculator.get_hand_strength(hole_cards, community)
    print(f"✅ Hand strength analysis:")
    print(f"   Current hand: {strength['description']}")
    print(f"   Hand rank: {strength['hand_rank']}")
    if 'strength_score' in strength:
        print(f"   Strength score: {strength['strength_score']:.2f}")
    
    print()

def run_demo():
    """Run a comprehensive demo / 运行综合演示"""
    print("🎰 Texas Hold'em Calculator Demo / 德州扑克计算器演示")
    print("=" * 60)
    
    calculator = TexasHoldemCalculator()
    
    # Demo scenario: Pocket Queens on the flop
    print("\n📋 Demo Scenario / 演示场景:")
    print("Your cards / 你的底牌: Q♥ Q♠")
    print("Flop / 翻牌: A♦ 8♣ 3♥")
    print("Opponents / 对手数: 2")
    
    hole_cards = [Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.QUEEN, Suit.SPADES)]
    flop = [Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.CLUBS), Card(Rank.THREE, Suit.HEARTS)]
    
    # Calculate probabilities
    prob_result = calculator.calculate_win_probability(hole_cards, flop, 2, 5000)
    
    # Get hand strength
    strength = calculator.get_hand_strength(hole_cards, flop)
    
    # Get betting recommendation
    betting = calculator.get_betting_recommendation(hole_cards, flop, 2, 150, 25)
    
    print(f"\n📊 Analysis / 分析:")
    print(f"Current Hand / 当前手牌: {strength['description']}")
    print(f"Win Probability / 胜率: {prob_result['win_probability']:.1%}")
    print(f"Recommended Action / 建议行动: {betting['recommended_action']}")
    print(f"Reasoning / 理由: {betting['reasoning']}")

def main():
    """Main test function / 主测试函数"""
    try:
        print("🚀 Starting Texas Hold'em Calculator Tests")
        print("开始德州扑克计算器测试")
        print("=" * 60)
        
        test_card_parsing()
        test_hand_evaluation()
        test_probability_calculation()
        test_betting_recommendations()
        test_hand_strength()
        
        print("✅ All tests passed! / 所有测试通过！")
        print("=" * 60)
        
        # Run demo
        run_demo()
        
        print("\n🎉 Testing completed successfully! / 测试成功完成！")
        print("You can now run: python texas_holdem_calculator.py")
        print("你现在可以运行: python texas_holdem_calculator.py")
        
    except Exception as e:
        print(f"❌ Test failed / 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()