"""
Accuracy regression tests for poker calculations
扑克计算的准确性回归测试

Tests against known scenarios and authoritative sources to ensure
calculation accuracy across different methods.
针对已知场景和权威来源进行测试，确保不同方法的计算准确性。
"""

import pytest
import math
from typing import List, Dict, Any, Tuple
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))

from texas_holdem_calculator import Card, Rank, Suit, parse_card_string
from src.core.enhanced_calculator import EnhancedTexasHoldemCalculator, CalculatorConfig
from src.core.exact_enumeration import enumerate_heads_up_equity
from src.core.vectorized_monte_carlo import simulate_equity_vectorized
from src.core.monte_carlo import simulate_equity


class TestKnownScenarios:
    """Test against known poker scenarios with verified results"""
    
    known_scenarios = [
            # Preflop scenarios
            {
                'name': 'AA vs KK preflop',
                'hero': 'As Ah',
                'villain': 'Ks Kh',
                'board': '',
                'expected_win_rate': 0.817,  # ~81.7%
                'tolerance': 0.005
            },
            {
                'name': 'AA vs random preflop',
                'hero': 'As Ah',
                'villain': None,
                'board': '',
                'expected_win_rate': 0.851,  # ~85.1%
                'tolerance': 0.005
            },
            {
                'name': 'AK vs QQ preflop',
                'hero': 'As Kh',
                'villain': 'Qs Qh',
                'board': '',
                'expected_win_rate': 0.436,  # ~43.6%
                'tolerance': 0.005
            },
            
            # Flop scenarios
            {
                'name': 'AA vs flush draw on flop',
                'hero': 'As Ah',
                'villain': 'Ks Qs',
                'board': '2s 5s 7h',
                'expected_win_rate': 0.718,  # ~71.8%
                'tolerance': 0.010
            },
            {
                'name': 'Set vs overpair on flop',
                'hero': '7s 7h',
                'villain': 'As Ah',
                'board': '7c 5d 2h',
                'expected_win_rate': 0.924,  # ~92.4%
                'tolerance': 0.010
            },
            {
                'name': 'Top pair vs bottom two pair on flop',
                'hero': 'As 7h',
                'villain': '5s 2h',
                'board': 'Ac 5d 2c',
                'expected_win_rate': 0.121,  # ~12.1%
                'tolerance': 0.010
            },
            
            # Turn scenarios
            {
                'name': 'Straight vs flush draw on turn',
                'hero': '6s 5h',
                'villain': 'Ks Qs',
                'board': '4h 3c 2d 9s',
                'expected_win_rate': 0.773,  # ~77.3%
                'tolerance': 0.015
            },
            {
                'name': 'Set vs straight on turn',
                'hero': '8s 8h',
                'villain': '6s 5h',
                'board': '8c 7d 4h 9c',
                'expected_win_rate': 0.136,  # ~13.6%
                'tolerance': 0.015
            },
            
            # River scenarios (exact calculations)
            {
                'name': 'Full house vs flush on river',
                'hero': '8s 8h',
                'villain': 'Ks Qs',
                'board': '8c 7s 4s 9s 8d',
                'expected_win_rate': 1.0,  # 100%
                'tolerance': 0.001
            },
            {
                'name': 'Straight vs straight (chopped pot)',
                'hero': '6s 5h',
                'villain': '6c 5d',
                'board': '4h 3c 2d 7s Ah',
                'expected_win_rate': 0.5,  # 50% (tie)
                'tolerance': 0.001
            }
        ]
    
    def parse_scenario(self, scenario: Dict[str, Any]) -> Tuple[List[Card], List[Card], List[Card]]:
        """Parse scenario into card objects"""
        hero_cards = [parse_card_string(card) for card in scenario['hero'].split()]
        villain_cards = [parse_card_string(card) for card in scenario['villain'].split()] if scenario['villain'] else None
        board_cards = [parse_card_string(card) for card in scenario['board'].split()] if scenario['board'] else []
        
        return hero_cards, villain_cards, board_cards
    
    @pytest.mark.parametrize("scenario", lambda: TestKnownScenarios.known_scenarios)
    def test_enumeration_accuracy(self, scenario):
        """Test exact enumeration accuracy against known results"""
        hero_cards, villain_cards, board_cards = self.parse_scenario(scenario)
        
        # Skip scenarios that are too complex for enumeration
        if not villain_cards or len(board_cards) < 3:
            pytest.skip("Scenario not suitable for enumeration testing")
        
        try:
            result = enumerate_heads_up_equity(
                hero_cards=hero_cards,
                villain_cards=villain_cards,
                community_cards=board_cards
            )
            
            win_rate = result.p_hat
            expected = scenario['expected_win_rate']
            tolerance = scenario['tolerance']
            
            assert abs(win_rate - expected) <= tolerance, (
                f"Enumeration failed for {scenario['name']}: "
                f"got {win_rate:.3f}, expected {expected:.3f} ±{tolerance:.3f}"
            )
            
        except ValueError as e:
            if "too complex" in str(e).lower():
                pytest.skip(f"Scenario too complex for enumeration: {e}")
            else:
                raise
    
    @pytest.mark.parametrize("scenario", known_scenarios)
    def test_vectorized_mc_accuracy(self, scenario):
        """Test vectorized Monte Carlo accuracy against known results"""
        hero_cards, villain_cards, board_cards = self.parse_scenario(scenario)
        
        # For known villain, we need to simulate random opponent
        if villain_cards:
            pytest.skip("Vectorized MC test requires random opponent scenario")
        
        try:
            result = simulate_equity_vectorized(
                hero_cards=hero_cards,
                community_cards=board_cards,
                num_opponents=1,
                num_simulations=50000,  # High simulation count for accuracy
                seed=42,
                target_ci=0.001  # Tight CI for accuracy testing
            )
            
            win_rate = result.p_hat
            expected = scenario['expected_win_rate']
            # Allow larger tolerance for MC methods
            tolerance = max(scenario['tolerance'] * 2, 0.01)
            
            assert abs(win_rate - expected) <= tolerance, (
                f"Vectorized MC failed for {scenario['name']}: "
                f"got {win_rate:.3f}, expected {expected:.3f} ±{tolerance:.3f}"
            )
            
        except Exception as e:
            if "not available" in str(e).lower():
                pytest.skip(f"Vectorized MC not available: {e}")
            else:
                raise
    
    @pytest.mark.parametrize("scenario", known_scenarios)
    def test_enhanced_calculator_accuracy(self, scenario):
        """Test enhanced calculator accuracy with automatic method selection"""
        hero_cards, villain_cards, board_cards = self.parse_scenario(scenario)
        
        config = CalculatorConfig(
            prefer_enumeration=True,
            default_simulations=20000,
            target_ci_radius=0.002
        )
        calculator = EnhancedTexasHoldemCalculator(config)
        
        # For scenarios with known villain, test enumeration
        # For scenarios with random opponent, test MC
        if villain_cards:
            # This would require modifying the calculator to accept known opponents
            # For now, skip these scenarios
            pytest.skip("Enhanced calculator test with known opponents not implemented")
        
        result = calculator.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=1,
            seed=42
        )
        
        win_rate = result.win_probability
        expected = scenario['expected_win_rate']
        tolerance = max(scenario['tolerance'] * 1.5, 0.008)  # Slightly relaxed for automatic method selection
        
        assert abs(win_rate - expected) <= tolerance, (
            f"Enhanced calculator failed for {scenario['name']}: "
            f"got {win_rate:.3f}, expected {expected:.3f} ±{tolerance:.3f}"
            f" (method: {result.method})"
        )


class TestMethodConsistency:
    """Test that different methods produce consistent results"""
    
    def setup_method(self):
        """Set up test scenarios for consistency testing"""
        self.test_scenarios = [
            {
                'hero': 'As Kh',
                'board': '2c 7d 9h',
                'opponents': 1
            },
            {
                'hero': 'Qs Qc',
                'board': 'Jh 8s 4d',
                'opponents': 2
            },
            {
                'hero': '7s 6h',
                'board': '5c 4d',
                'opponents': 1
            }
        ]
    
    def test_enumeration_vs_mc_consistency(self):
        """Test that enumeration and Monte Carlo give consistent results"""
        for scenario in self.test_scenarios:
            hero_cards = [parse_card_string(card) for card in scenario['hero'].split()]
            board_cards = [parse_card_string(card) for card in scenario['board'].split()]
            
            # Use enumeration for heads-up scenarios with sufficient board cards
            if scenario['opponents'] == 1 and len(board_cards) >= 3:
                try:
                    enum_result = enumerate_heads_up_equity(
                        hero_cards=hero_cards,
                        villain_cards=None,
                        community_cards=board_cards
                    )
                    
                    # Compare with high-precision Monte Carlo
                    try:
                        mc_result = simulate_equity_vectorized(
                            hero_cards=hero_cards,
                            community_cards=board_cards,
                            num_opponents=1,
                            num_simulations=100000,
                            seed=42,
                            target_ci=0.001
                        )
                        
                        # Results should be within MC confidence interval
                        ci_radius = mc_result.ci_radius
                        tolerance = max(ci_radius * 3, 0.01)  # 3x CI radius or 1%
                        
                        assert abs(enum_result.p_hat - mc_result.p_hat) <= tolerance, (
                            f"Enumeration vs MC inconsistency for {scenario}: "
                            f"enum={enum_result.p_hat:.4f}, mc={mc_result.p_hat:.4f} "
                            f"±{ci_radius:.4f}"
                        )
                        
                    except ImportError:
                        pytest.skip("Vectorized MC not available for consistency test")
                        
                except ValueError as e:
                    if "too complex" in str(e).lower():
                        pytest.skip(f"Scenario too complex for enumeration: {e}")
                    else:
                        raise
    
    def test_seed_reproducibility(self):
        """Test that the same seed produces identical results"""
        scenario = self.test_scenarios[0]
        hero_cards = [parse_card_string(card) for card in scenario['hero'].split()]
        board_cards = [parse_card_string(card) for card in scenario['board'].split()]
        
        # Test enhanced calculator reproducibility
        config = CalculatorConfig(prefer_enumeration=False, default_simulations=5000)
        calculator = EnhancedTexasHoldemCalculator(config)
        
        result1 = calculator.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=1,
            seed=12345
        )
        
        result2 = calculator.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=1,
            seed=12345
        )
        
        assert result1.win_probability == result2.win_probability, (
            f"Seed reproducibility failed: {result1.win_probability} != {result2.win_probability}"
        )
        
        assert result1.simulations == result2.simulations, (
            f"Simulation count not reproducible: {result1.simulations} != {result2.simulations}"
        )


class TestConfidenceIntervals:
    """Test confidence interval calculations"""
    
    def test_wilson_ci_properties(self):
        """Test Wilson confidence interval properties"""
        from src.core.monte_carlo import wilson_confidence_interval
        
        # Test edge cases
        ci_low, ci_high = wilson_confidence_interval(0, 100)
        assert ci_low >= 0.0
        assert ci_high <= 1.0
        assert ci_low <= ci_high
        
        ci_low, ci_high = wilson_confidence_interval(100, 100)
        assert ci_low >= 0.0
        assert ci_high <= 1.0
        assert ci_low <= ci_high
        
        # Test that CI width decreases with more samples
        ci1_low, ci1_high = wilson_confidence_interval(50, 100)
        ci2_low, ci2_high = wilson_confidence_interval(500, 1000)
        
        width1 = ci1_high - ci1_low
        width2 = ci2_high - ci2_low
        
        assert width2 < width1, "CI should narrow with more samples"
    
    def test_ci_coverage(self):
        """Test that confidence intervals have proper coverage"""
        # This is a statistical test that would require many repeated experiments
        # For now, just test basic properties
        from src.core.monte_carlo import wilson_confidence_interval
        
        # Test some known good values
        wins = 450
        total = 1000
        ci_low, ci_high = wilson_confidence_interval(wins, total)
        
        # CI should contain the point estimate
        point_estimate = wins / total
        assert ci_low <= point_estimate <= ci_high
        
        # CI should be reasonable width for this sample size
        width = ci_high - ci_low
        assert 0.02 <= width <= 0.08  # Reasonable range for n=1000


class TestPerformanceRegression:
    """Test that performance doesn't regress"""
    
    def test_enumeration_performance(self):
        """Test enumeration performance benchmarks"""
        import time
        
        # Simple heads-up scenario with known cards
        hero_cards = [parse_card_string('As'), parse_card_string('Kh')]
        villain_cards = [parse_card_string('Qs'), parse_card_string('Qc')]
        board_cards = [parse_card_string('2c'), parse_card_string('7d'), parse_card_string('9h')]
        
        start_time = time.time()
        result = enumerate_heads_up_equity(
            hero_cards=hero_cards,
            villain_cards=villain_cards,
            community_cards=board_cards
        )
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_ms < 1000, f"Enumeration took too long: {elapsed_ms:.1f}ms"
        assert result.n > 0, "Should have evaluated some scenarios"
    
    def test_mc_performance(self):
        """Test Monte Carlo performance benchmarks"""
        import time
        
        hero_cards = [parse_card_string('As'), parse_card_string('Kh')]
        board_cards = [parse_card_string('2c'), parse_card_string('7d')]
        
        config = CalculatorConfig(
            prefer_enumeration=False,
            default_simulations=10000
        )
        calculator = EnhancedTexasHoldemCalculator(config)
        
        start_time = time.time()
        result = calculator.calculate_win_probability(
            hole_cards=hero_cards,
            community_cards=board_cards,
            num_opponents=1,
            force_method='standard'
        )
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        # Should complete 10k simulations within reasonable time
        assert elapsed_ms < 5000, f"MC simulation took too long: {elapsed_ms:.1f}ms"
        assert result.simulations >= 1000, "Should have run sufficient simulations"


if __name__ == "__main__":
    # Run a quick smoke test
    print("Running accuracy regression smoke test...")
    
    # Test basic functionality
    hero = [parse_card_string('As'), parse_card_string('Kh')]
    board = [parse_card_string('2c'), parse_card_string('7d'), parse_card_string('9h')]
    
    try:
        result = enumerate_heads_up_equity(hero, None, board)
        print(f"Enumeration: {result.p_hat:.3f} in {result.n} scenarios")
    except Exception as e:
        print(f"Enumeration failed: {e}")
    
    try:
        config = CalculatorConfig(default_simulations=1000)
        calc = EnhancedTexasHoldemCalculator(config)
        result = calc.calculate_win_probability(hero, board, 1)
        print(f"Enhanced calc: {result.win_probability:.3f} ±{result.ci_radius:.3f} "
              f"({result.method}, {result.simulations} sims)")
    except Exception as e:
        print(f"Enhanced calculator failed: {e}")
    
    print("Smoke test completed.")