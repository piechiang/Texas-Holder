"""
Tests for exact enumeration and automatic method selection
精确枚举和自动方法选择测试
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to import modules
sys.path.append(str(Path(__file__).parent))

from texas_holdem_calculator import parse_card_string
from src.core.enumeration import PokerEnumerator, enumerate_equity
from src.core.dispatcher import EquityDispatcher, compute_equity
from src.core.monte_carlo import simulate_equity


def test_enum_matches_mc_preflop():
    """Test that enumeration gives reasonable results for known hands on flop"""
    # Parse cards - use flop scenario for manageable complexity
    hero_cards = [parse_card_string("As"), parse_card_string("Ks")]
    villain_cards = [parse_card_string("Qh"), parse_card_string("Qs")]
    community_cards = [
        parse_card_string("2c"),
        parse_card_string("7h"),
        parse_card_string("Jd")
    ]
    
    # Exact enumeration on flop
    enum_result = enumerate_equity(
        hero_cards=hero_cards,
        opponent_cards=[villain_cards],  # One known opponent
        community_cards=community_cards
    )
    
    # Check that enumeration gives reasonable result
    # AK vs QQ on this flop (QQ overpair, AK has some outs)
    assert 0.20 <= enum_result.p_hat <= 0.35, f"AK vs QQ on this flop should be ~25%, got {enum_result.p_hat:.1%}"
    assert enum_result.mode == "ENUM", "Should use enumeration"
    assert enum_result.ci_radius == 0.0, "Enumeration should have zero CI radius"
    assert enum_result.n > 100, "Should enumerate reasonable number of scenarios"


def test_auto_switch_to_enum():
    """Test that auto-selection chooses enumeration for small scenarios"""
    dispatcher = EquityDispatcher()
    
    # Single known opponent with flop (should use enumeration)
    hero_cards = [parse_card_string("Ah"), parse_card_string("Ad")]
    opponent_specs = [
        [parse_card_string("Kh"), parse_card_string("Ks")]  # Known opponent
    ]
    community_cards = [
        parse_card_string("2c"),
        parse_card_string("7h"), 
        parse_card_string("Jd")
    ]
    
    result = compute_equity(
        hero_cards=hero_cards,
        opponent_specs=opponent_specs,
        community_cards=community_cards,
        auto=True,
        verbose=False
    )
    
    # Should use enumeration for this small scenario
    assert result.mode == "ENUM", f"Expected ENUM mode, got {result.mode}"
    assert result.ci_radius == 0.0, "Enumeration should have zero CI radius"
    assert 0.85 <= result.p_hat <= 0.95, f"AA vs KK on safe board should win ~90%, got {result.p_hat:.1%}"


def test_backoff_to_mc_when_players_gt2():
    """Test that system falls back to MC when too many players"""
    dispatcher = EquityDispatcher()
    
    # Three random opponents (should use Monte Carlo)
    hero_cards = [parse_card_string("Js"), parse_card_string("Jd")]
    opponent_specs = ["random", "random", "random"]  # 3 random opponents
    
    result = compute_equity(
        hero_cards=hero_cards,
        opponent_specs=opponent_specs,
        community_cards=[],
        target_ci=0.02,  # Relaxed CI for faster test
        max_iter=5000,   # Limited iterations for test speed
        auto=True,
        verbose=False
    )
    
    # Should use Monte Carlo for this larger scenario
    assert result.mode == "MC", f"Expected MC mode, got {result.mode}"
    assert result.ci_radius > 0.0, "Monte Carlo should have non-zero CI radius"
    assert 0.3 <= result.p_hat <= 0.6, f"JJ vs 3 randoms should be ~40-50%, got {result.p_hat:.1%}"


def test_enumeration_complexity_limits():
    """Test that enumeration rejects overly complex scenarios"""
    enumerator = PokerEnumerator()
    
    # Test decision function
    # Should reject: many opponents
    assert not enumerator.should_use_enumeration(
        num_total_opponents=5,
        num_known_opponents=0,
        num_community_cards=0
    ), "Should reject 5 opponents"
    
    # Should reject: many random opponents
    assert not enumerator.should_use_enumeration(
        num_total_opponents=3,
        num_known_opponents=0,  # 3 random opponents
        num_community_cards=0
    ), "Should reject 3 random opponents"
    
    # Should accept: heads-up with known cards
    assert enumerator.should_use_enumeration(
        num_total_opponents=1,
        num_known_opponents=1,
        num_community_cards=3
    ), "Should accept heads-up with known villain on flop"
    
    # Should accept: heads-up random on river
    assert enumerator.should_use_enumeration(
        num_total_opponents=1,
        num_known_opponents=0,
        num_community_cards=5
    ), "Should accept heads-up random on river"


def test_enumeration_error_handling():
    """Test error handling for invalid enumeration scenarios"""
    
    # Test invalid hero cards
    with pytest.raises(ValueError, match="Hero must have exactly 2"):
        enumerate_equity(
            hero_cards=[parse_card_string("As")],  # Only 1 card
            opponent_cards=[None],
            community_cards=[]
        )
    
    # Test invalid opponent cards
    with pytest.raises(ValueError, match="must have exactly 2"):
        enumerate_equity(
            hero_cards=[parse_card_string("As"), parse_card_string("Ks")],
            opponent_cards=[[parse_card_string("Qh")]],  # Only 1 card for opponent
            community_cards=[]
        )
    
    # Test card conflicts (same card for hero and opponent)
    with pytest.raises(Exception):  # Should fail due to card conflict
        hero_cards = [parse_card_string("As"), parse_card_string("Ks")]
        villain_cards = [parse_card_string("As"), parse_card_string("Qh")]  # Conflict: As
        
        enumerate_equity(
            hero_cards=hero_cards,
            opponent_cards=[villain_cards],
            community_cards=[]
        )


def test_dispatcher_force_methods():
    """Test that dispatcher respects forced method selection"""
    hero_cards = [parse_card_string("Ac"), parse_card_string("Ad")]
    opponent_specs = [
        [parse_card_string("Kh"), parse_card_string("Ks")]  # Known opponent for manageable enum
    ]
    community_cards = [
        parse_card_string("2c"),
        parse_card_string("7h"),
        parse_card_string("Jd")
    ]
    
    dispatcher = EquityDispatcher()
    
    # Force enumeration (should work with flop scenario)
    result_enum = dispatcher.compute_equity(
        hero_cards=hero_cards,
        opponent_specs=opponent_specs,
        community_cards=community_cards,
        force_method="enum",
        verbose=False
    )
    assert result_enum.mode == "ENUM", "Should respect forced enumeration"
    
    # Force Monte Carlo
    result_mc = dispatcher.compute_equity(
        hero_cards=hero_cards,
        opponent_specs=opponent_specs,
        community_cards=community_cards,
        force_method="mc",
        target_ci=0.02,
        max_iter=2000,
        verbose=False
    )
    assert result_mc.mode == "MC", "Should respect forced Monte Carlo"
    
    # Results should be reasonably close (both calculating AA vs KK on same board)
    # Note: MC may have some variance even with 2000 samples
    equity_diff = abs(result_enum.p_hat - result_mc.p_hat)
    assert equity_diff <= 0.10, f"ENUM and MC should give similar results, diff: {equity_diff:.3f}"
    
    # More importantly, both should show AA is significantly ahead
    assert result_enum.p_hat >= 0.85, f"AA should dominate vs KK, enum: {result_enum.p_hat:.1%}"
    assert result_mc.p_hat >= 0.75, f"AA should dominate vs KK, MC: {result_mc.p_hat:.1%}"


def test_enumeration_heads_up_known():
    """Test enumeration with heads-up known hands"""
    # Pocket Aces vs Pocket Kings on flop (manageable complexity)
    hero_cards = [parse_card_string("As"), parse_card_string("Ad")]
    villain_cards = [parse_card_string("Kh"), parse_card_string("Ks")]
    
    # Test with flop (more manageable than preflop)
    result_flop = enumerate_equity(
        hero_cards=hero_cards,
        opponent_cards=[villain_cards],
        community_cards=[
            parse_card_string("2c"),
            parse_card_string("7h"),
            parse_card_string("Jd")
        ]
    )
    
    # AA vs KK on this board should be ~91% for AA
    assert 0.88 <= result_flop.p_hat <= 0.95, f"AA vs KK on safe board should be ~91%, got {result_flop.p_hat:.1%}"
    assert result_flop.mode == "ENUM"
    assert result_flop.n > 100, "Should enumerate reasonable scenarios for flop"
    
    # Test with turn (even fewer scenarios)
    result_turn = enumerate_equity(
        hero_cards=hero_cards,
        opponent_cards=[villain_cards],
        community_cards=[
            parse_card_string("2c"),
            parse_card_string("7h"),
            parse_card_string("Jd"),
            parse_card_string("3s")
        ]
    )
    
    assert result_turn.mode == "ENUM"
    assert result_turn.n < result_flop.n, "Turn should have fewer scenarios than flop"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])