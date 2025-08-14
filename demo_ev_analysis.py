#!/usr/bin/env python3
"""
Demo script showcasing EV calculation and break-even analysis
演示EV计算和盈亏平衡分析功能
"""

from texas_holdem_calculator import parse_card_string
from src.strategy.ev_calculator import (
    EVCalculator, EVScenario, quick_ev_analysis,
    calculate_breakeven_analysis
)

def demo_basic_ev_calculation():
    """Demonstrate basic EV calculation scenarios"""
    print("🎯 Basic EV Calculation Demo")
    print("基础EV计算演示")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Premium Hand vs Random (Preflop)",
            "hero": "AA",
            "villain": "random",
            "board": [],
            "pot": 100,
            "bet": 25,
            "description": "Pocket Aces facing a small bet preflop"
        },
        {
            "name": "Medium Hand vs Tight Range (Flop)",
            "hero": "JJ",
            "villain": "TT+, AQs+",
            "board": [parse_card_string("9h"), parse_card_string("7c"), parse_card_string("2d")],
            "pot": 150,
            "bet": 75,
            "description": "Pocket Jacks on a dry flop vs tight range"
        },
        {
            "name": "Drawing Hand vs Wide Range (Turn)",
            "hero": "A5s",
            "villain": "22+, ATo+, KQo, 54s+",
            "board": [parse_card_string("Kh"), parse_card_string("8d"), parse_card_string("7s"), parse_card_string("6c")],
            "pot": 200,
            "bet": 120,
            "description": "Ace-high with straight draw vs wide range on turn"
        }
    ]
    
    calculator = EVCalculator()
    
    for i, scenario in enumerate(scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Hero: {scenario['hero']} vs Villain: {scenario['villain']}")
        if scenario['board']:
            board_str = " ".join(str(card) for card in scenario['board'])
            print(f"   Board: {board_str}")
        print(f"   Pot: ${scenario['pot']}, Bet to call: ${scenario['bet']}")
        
        try:
            result = quick_ev_analysis(
                hero_range=scenario['hero'],
                villain_range=scenario['villain'],
                community_cards=scenario['board'],
                pot_size=scenario['pot'],
                bet_to_call=scenario['bet'],
                stack_size=500,
                verbose=False
            )
            
            print(f"   📊 Results:")
            print(f"      Equity: {result.equity_result.p_hat:.1%}")
            print(f"      EV(Call): ${result.ev_call:.2f}")
            print(f"      EV(All-in): ${result.ev_all_in:.2f}" if result.ev_all_in else "      EV(All-in): N/A")
            print(f"      Recommendation: {result.recommended_action.value.upper()}")
            print(f"      Confidence: {result.confidence_level}")
            
            if result.breakeven_analysis:
                ba = result.breakeven_analysis
                print(f"      Pot Odds: {ba.pot_odds:.1%} (need {ba.required_equity:.1%} equity)")
                print(f"      Equity Surplus: {ba.equity_surplus:+.1%}")
                print(f"      Kelly Criterion: {ba.kelly_criterion:.3f}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def demo_breakeven_analysis():
    """Demonstrate detailed break-even analysis"""
    print(f"\n\n⚖️  Break-even Analysis Demo")
    print("盈亏平衡分析演示")
    print("=" * 60)
    
    scenarios = [
        {"pot": 100, "bet": 20, "equity": 0.30, "desc": "Easy call (30% vs 16.7% required)"},
        {"pot": 100, "bet": 50, "equity": 0.35, "desc": "Marginal call (35% vs 33.3% required)"},
        {"pot": 100, "bet": 75, "equity": 0.40, "desc": "Tough spot (40% vs 42.9% required)"},
        {"pot": 100, "bet": 90, "equity": 0.45, "desc": "Clear fold (45% vs 47.4% required)"},
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['desc']}")
        print(f"   Pot: ${scenario['pot']}, Bet: ${scenario['bet']}, Equity: {scenario['equity']:.1%}")
        
        analysis = calculate_breakeven_analysis(
            pot_size=scenario['pot'],
            bet_to_call=scenario['bet'],
            current_equity=scenario['equity']
        )
        
        print(f"   📊 Analysis:")
        print(f"      Pot Odds: {analysis.pot_odds:.1%}")
        print(f"      Required Equity: {analysis.required_equity:.1%}")
        print(f"      Equity Surplus: {analysis.equity_surplus:+.1%}")
        print(f"      Risk/Reward: {analysis.risk_reward_ratio:.2f}:1")
        print(f"      Kelly Criterion: {analysis.kelly_criterion:.3f}")
        print(f"      Decision: {analysis.decision_confidence}")
        print(f"      Assessment: {analysis.recommendation_reason}")


def demo_advanced_scenarios():
    """Demonstrate advanced EV scenarios with raises and implied odds"""
    print(f"\n\n🚀 Advanced EV Scenarios Demo")
    print("高级EV场景演示")
    print("=" * 60)
    
    # Scenario 1: Raise vs Call decision
    print(f"\n📋 Scenario 1: Raise vs Call Decision")
    print(f"   Strong hand considering raise for value")
    
    scenario = EVScenario(
        hero_range="KK",
        villain_ranges=["22+, ATo+, KQo"],
        community_cards=[parse_card_string("Qh"), parse_card_string("7c"), parse_card_string("2s")],
        pot_size=120,
        bet_to_call=40,
        stack_size=300
    )
    
    calculator = EVCalculator()
    result = calculator.calculate_ev(
        scenario=scenario,
        raise_size=120,  # Pot-sized raise
        fold_equity=0.25,  # 25% chance villain folds
        verbose=False
    )
    
    print(f"   📊 Results:")
    print(f"      Equity: {result.equity_result.p_hat:.1%}")
    print(f"      EV(Call): ${result.ev_call:.2f}")
    print(f"      EV(Raise): ${result.ev_raise:.2f}")
    print(f"      Best Action: {result.recommended_action.value.upper()}")
    print(f"      Reasoning: {result.reasoning}")
    
    # Scenario 2: Implied odds consideration
    print(f"\n📋 Scenario 2: Implied Odds Consideration")
    print(f"   Drawing hand with deep stacks")
    
    scenario2 = EVScenario(
        hero_range="87s",  # Straight draw
        villain_ranges=["TT+, AQs+, KQo"],
        community_cards=[parse_card_string("9h"), parse_card_string("6c"), parse_card_string("2d")],
        pot_size=60,
        bet_to_call=45,
        stack_size=400
    )
    
    result2 = calculator.calculate_ev(
        scenario=scenario2,
        implied_odds_multiplier=2.5,  # Expect to win 2.5x more when hitting
        verbose=False
    )
    
    print(f"   📊 Results:")
    print(f"      Equity: {result2.equity_result.p_hat:.1%}")
    print(f"      EV(Call): ${result2.ev_call:.2f}")
    print(f"      Action: {result2.recommended_action.value.upper()}")
    print(f"      Reasoning: {result2.reasoning}")
    
    if result2.breakeven_analysis:
        ba = result2.breakeven_analysis
        print(f"      Implied Odds: {ba.implied_odds:.1%}")
        print(f"      Future Pot Potential: ${ba.future_pot_potential:.0f}")


def demo_range_vs_range_ev():
    """Demonstrate range vs range EV analysis"""
    print(f"\n\n⚔️  Range vs Range EV Demo")
    print("范围对范围EV演示")
    print("=" * 60)
    
    matchups = [
        {
            "name": "Preflop 3-bet Spot",
            "hero": "JJ+, AKs, AQs",
            "villain": "TT+, AQs+, AKo",
            "board": [],
            "pot": 150,
            "bet": 100,
            "desc": "Hero 3-bets, villain 4-bets"
        },
        {
            "name": "Flop Continuation Bet",
            "hero": "AA, KK, AKs, AQs",
            "villain": "22+, ATs+, KQo, 98s+",
            "board": [parse_card_string("As"), parse_card_string("7h"), parse_card_string("3c")],
            "pot": 80,
            "bet": 55,
            "desc": "Ace-high flop, hero cbets"
        }
    ]
    
    calculator = EVCalculator()
    
    for i, matchup in enumerate(matchups):
        print(f"\n📋 Matchup {i+1}: {matchup['name']}")
        print(f"   {matchup['desc']}")
        print(f"   Hero Range: {matchup['hero']}")
        print(f"   Villain Range: {matchup['villain']}")
        if matchup['board']:
            board_str = " ".join(str(card) for card in matchup['board'])
            print(f"   Board: {board_str}")
        print(f"   Pot: ${matchup['pot']}, Bet: ${matchup['bet']}")
        
        try:
            result = quick_ev_analysis(
                hero_range=matchup['hero'],
                villain_range=matchup['villain'],
                community_cards=matchup['board'],
                pot_size=matchup['pot'],
                bet_to_call=matchup['bet'],
                stack_size=500,
                verbose=False
            )
            
            print(f"   📊 Results:")
            print(f"      Hero Equity: {result.equity_result.p_hat:.1%}")
            print(f"      Required Equity: {result.breakeven_equity:.1%}")
            print(f"      EV(Call): ${result.ev_call:.2f}")
            print(f"      Recommendation: {result.recommended_action.value.upper()}")
            print(f"      Confidence: {result.confidence_level}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Run all EV analysis demos"""
    print("🎯 Texas Hold'em EV Analysis Demo")
    print("德州扑克EV分析演示")
    print("=" * 80)
    
    demo_basic_ev_calculation()
    demo_breakeven_analysis()
    demo_advanced_scenarios()
    demo_range_vs_range_ev()
    
    print(f"\n\n🏆 Key Features Demonstrated:")
    print("=" * 80)
    print("✅ Expected Value calculation for Call, Raise, All-in actions")
    print("✅ Comprehensive break-even analysis with pot odds")
    print("✅ Kelly Criterion for optimal bet sizing")
    print("✅ Implied odds and reverse implied odds")
    print("✅ Range vs Range equity calculation")
    print("✅ Decision confidence levels and reasoning")
    print("✅ Risk/reward ratio analysis")
    print("✅ Multi-street betting considerations")
    print("✅ Position and stack depth factors")
    print("✅ Advanced scenarios with fold equity")
    
    print(f"\n💡 This EV calculator provides professional-grade analysis for:")
    print("   • Cash game decision making")
    print("   • Tournament spot evaluation")
    print("   • Training and study scenarios")
    print("   • Range construction and refinement")
    print("   • Bankroll management with Kelly Criterion")


if __name__ == "__main__":
    main()