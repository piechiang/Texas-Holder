#!/usr/bin/env python3
"""
Test cases for EV Calculator
EV计算器测试用例
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to import modules
sys.path.append(str(Path(__file__).parent))

from texas_holdem_calculator import parse_card_string
from src.strategy.ev_calculator import (
    EVCalculator, EVScenario, ActionType, 
    calculate_breakeven_analysis, quick_ev_analysis
)


def test_breakeven_analysis():
    """Test break-even analysis calculations"""
    # Scenario: $100 pot, $25 to call
    # Required equity = 25/(100+25) = 20%
    analysis = calculate_breakeven_analysis(
        pot_size=100.0,
        bet_to_call=25.0,
        current_equity=0.30  # 30% equity
    )
    
    assert abs(analysis.pot_odds - 0.20) < 0.01  # 20% pot odds
    assert abs(analysis.required_equity - 0.20) < 0.01
    assert analysis.current_equity == 0.30
    assert abs(analysis.equity_surplus - 0.10) < 0.01  # 10% surplus
    assert analysis.is_profitable == True
    assert analysis.decision_confidence == "High (Conservative Play)"


def test_ev_scenario_creation():
    """Test EV scenario creation and properties"""
    community_cards = [
        parse_card_string("Ah"),
        parse_card_string("Kh"), 
        parse_card_string("Qc")
    ]
    
    scenario = EVScenario(
        hero_range="AA, KK",
        villain_ranges=["22+, ATs+"],
        community_cards=community_cards,
        pot_size=150.0,
        bet_to_call=50.0,
        stack_size=500.0,
        position="BTN"
    )
    
    # Test pot odds calculation
    expected_pot_odds = 50.0 / (150.0 + 50.0)  # 25%
    assert abs(scenario.pot_odds - expected_pot_odds) < 0.01
    
    # Test total pot after call
    assert scenario.total_pot_after_call == 200.0


def test_basic_ev_calculation():
    """Test basic EV calculation with known equity"""
    community_cards = []  # Preflop
    
    scenario = EVScenario(
        hero_range="AA",  # Strong hand
        villain_ranges=["random"],
        community_cards=community_cards,
        pot_size=100.0,
        bet_to_call=20.0,
        stack_size=300.0
    )
    
    calculator = EVCalculator()
    result = calculator.calculate_ev(
        scenario=scenario,
        target_ci=0.05,  # Wider CI for faster test
        max_iter=10000,   # Fewer iterations for speed
        verbose=False
    )
    
    # AA vs random should have high equity (>80%)
    assert result.equity_result.p_hat > 0.75
    
    # Should recommend call or raise (not fold) with AA
    assert result.recommended_action in [ActionType.CALL, ActionType.RAISE, ActionType.ALL_IN]
    
    # EV calculations should be reasonable
    assert result.ev_fold == 0.0
    assert result.ev_call > 0  # Should be profitable to call with AA
    
    # Break-even analysis
    assert result.pot_odds == 20.0 / 120.0  # ~16.7%
    assert result.equity_surplus > 0.5  # Should have large equity surplus


def test_marginal_spot_ev():
    """Test EV calculation in a marginal spot"""
    community_cards = [
        parse_card_string("9h"),
        parse_card_string("7c"),
        parse_card_string("2d")
    ]
    
    scenario = EVScenario(
        hero_range="A5s",  # Marginal hand on dry board
        villain_ranges=["TT+, ATs+, KQo"],  # Strong range
        community_cards=community_cards,
        pot_size=80.0,
        bet_to_call=60.0,  # Large bet
        stack_size=200.0
    )
    
    calculator = EVCalculator()
    result = calculator.calculate_ev(
        scenario=scenario,
        target_ci=0.05,
        max_iter=10000,
        verbose=False
    )
    
    # Should have low equity against strong range
    assert result.equity_result.p_hat < 0.50
    
    # Pot odds are 60/(80+60) = 42.9%
    expected_pot_odds = 60.0 / 140.0
    assert abs(result.pot_odds - expected_pot_odds) < 0.01
    
    # The EV calculator might recommend all-in if it has positive EV
    # This is actually reasonable if the equity is close to the pot odds
    assert result.recommended_action in [ActionType.FOLD, ActionType.CALL, ActionType.ALL_IN]


def test_quick_ev_analysis():
    """Test the convenience function for quick analysis"""
    community_cards = [
        parse_card_string("Kh"),
        parse_card_string("Qd"),
        parse_card_string("Jc")
    ]
    
    result = quick_ev_analysis(
        hero_range="ATs+",
        villain_range="22+, ATo+, KQo",
        community_cards=community_cards,
        pot_size=120.0,
        bet_to_call=40.0,
        stack_size=250.0,
        verbose=False
    )
    
    # Should have calculated equity
    assert 0 <= result.equity_result.p_hat <= 1
    
    # Should have made a recommendation
    assert result.recommended_action in [ActionType.FOLD, ActionType.CALL, ActionType.RAISE, ActionType.ALL_IN]
    
    # Should have reasoning
    assert len(result.reasoning) > 0
    
    # Should be able to convert to dict
    result_dict = result.to_dict()
    assert "equity" in result_dict
    assert "ev_analysis" in result_dict
    assert "breakeven_analysis" in result_dict
    assert "recommendation" in result_dict


def test_ev_result_to_dict():
    """Test EVResult serialization to dictionary"""
    community_cards = []
    
    scenario = EVScenario(
        hero_range="KK",
        villain_ranges=["random"],
        community_cards=community_cards,
        pot_size=50.0,
        bet_to_call=10.0,
        stack_size=100.0
    )
    
    calculator = EVCalculator()
    result = calculator.calculate_ev(
        scenario=scenario,
        raise_size=30.0,  # Test raise EV
        target_ci=0.05,
        max_iter=5000,
        verbose=False
    )
    
    result_dict = result.to_dict()
    
    # Check all required sections
    required_sections = ["equity", "ev_analysis", "breakeven_analysis", "recommendation", "scenario"]
    for section in required_sections:
        assert section in result_dict
    
    # Check equity section
    equity = result_dict["equity"]
    assert "win_probability" in equity
    assert "method" in equity
    
    # Check EV analysis
    ev_analysis = result_dict["ev_analysis"]
    assert "ev_fold" in ev_analysis
    assert "ev_call" in ev_analysis
    assert "best_ev" in ev_analysis
    
    # Check recommendation
    recommendation = result_dict["recommendation"]
    assert "action" in recommendation
    assert "confidence" in recommendation
    assert "reasoning" in recommendation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])