#!/usr/bin/env python3
"""
Quick demo of the Texas Hold'em Calculator
德州扑克计算器快速演示
"""

from texas_holdem_calculator import TexasHoldemCalculator, parse_card_string

def demo():
    calculator = TexasHoldemCalculator()
    
    print("🎰 Texas Hold'em Calculator Quick Demo")
    print("德州扑克计算器快速演示")
    print("=" * 50)
    
    # Example 1: Strong starting hand
    print("\n📝 Example 1: Strong Starting Hand / 强起手牌")
    print("Hole cards: As Ah (Pocket Aces)")
    
    hole_cards = [parse_card_string('As'), parse_card_string('Ah')]
    
    prob_result = calculator.calculate_win_probability(hole_cards, [], 1, 5000)
    betting = calculator.get_betting_recommendation(hole_cards, [], 1, 100, 10)
    
    print(f"Win probability: {prob_result['win_probability']:.1%}")
    print(f"Recommendation: {betting['recommended_action']} ({betting['confidence']})")
    print(f"Reasoning: {betting['reasoning']}")
    
    # Example 2: Marginal hand with community cards
    print("\n📝 Example 2: Marginal Hand on Flop / 翻牌圈边际手牌")
    print("Hole cards: Jh 10s")
    print("Community: 9c 8d 2h")
    
    hole_cards2 = [parse_card_string('Jh'), parse_card_string('10s')]
    community = [parse_card_string('9c'), parse_card_string('8d'), parse_card_string('2h')]
    
    prob_result2 = calculator.calculate_win_probability(hole_cards2, community, 1, 5000)
    strength = calculator.get_hand_strength(hole_cards2, community)
    betting2 = calculator.get_betting_recommendation(hole_cards2, community, 1, 80, 20)
    
    print(f"Current hand: {strength['description']}")
    print(f"Win probability: {prob_result2['win_probability']:.1%}")
    print(f"Recommendation: {betting2['recommended_action']} ({betting2['confidence']})")
    print(f"Drawing potential: Open-ended straight draw")
    
    # Example 3: Made hand
    print("\n📝 Example 3: Strong Made Hand / 强成牌")
    print("Hole cards: Kc Kd")
    print("Community: Ks 4h 4c")
    
    hole_cards3 = [parse_card_string('Kc'), parse_card_string('Kd')]
    community3 = [parse_card_string('Ks'), parse_card_string('4h'), parse_card_string('4c')]
    
    strength3 = calculator.get_hand_strength(hole_cards3, community3)
    prob_result3 = calculator.calculate_win_probability(hole_cards3, community3, 2, 5000)
    betting3 = calculator.get_betting_recommendation(hole_cards3, community3, 2, 200, 50)
    
    print(f"Current hand: {strength3['description']}")
    print(f"Win probability vs 2 opponents: {prob_result3['win_probability']:.1%}")
    print(f"Recommendation: {betting3['recommended_action']} ({betting3['confidence']})")
    
    print("\n🎉 Demo completed! Run 'python texas_holdem_calculator.py' for interactive mode.")

if __name__ == "__main__":
    demo()