"""
Tests for Monte Carlo confidence intervals and early stopping
蒙特卡罗置信区间和早停测试
"""

import pytest
import math
from src.core.monte_carlo import (
    simulate_equity, 
    wilson_confidence_interval, 
    normal_confidence_interval,
    calculate_required_samples
)
from src.core.equity_result import EquityResult


def test_mc_ci_converges_mid_p():
    """Test CI convergence for p≈0.5 scenario"""
    def simulate_coinflip():
        import random
        win = random.random() < 0.5
        return win, False  # No ties for simple test
    
    result = simulate_equity(
        simulate_once_fn=simulate_coinflip,
        target_ci=0.01,  # ±1%
        max_iter=20000,
        seed=42
    )
    
    # Should converge around n≈9,600 for p≈0.5 with ±1% CI
    assert result.n >= 100, "Should have at least 100 samples"
    assert result.ci_radius <= 0.011, f"CI radius {result.ci_radius:.4f} should be ≤ 0.011"
    assert 0.4 <= result.p_hat <= 0.6, f"p_hat {result.p_hat:.3f} should be around 0.5"
    assert result.mode == "MC"


def test_mc_ci_converges_low_p():
    """Test CI convergence for p≈0.1 scenario"""
    def simulate_low_prob():
        import random
        win = random.random() < 0.1
        return win, False
    
    result = simulate_equity(
        simulate_once_fn=simulate_low_prob,
        target_ci=0.005,  # ±0.5%
        max_iter=100000,
        seed=123
    )
    
    assert result.n >= 100, "Should have at least 100 samples"
    assert result.ci_radius <= 0.006, f"CI radius {result.ci_radius:.4f} should be ≤ 0.006"
    assert 0.05 <= result.p_hat <= 0.15, f"p_hat {result.p_hat:.3f} should be around 0.1"


def test_mc_seed_reproducible():
    """Test that same seed produces identical results"""
    def simulate_coinflip():
        import random
        win = random.random() < 0.5
        return win, False
    
    result1 = simulate_equity(
        simulate_once_fn=simulate_coinflip,
        target_ci=0.02,
        max_iter=5000,
        seed=999
    )
    
    result2 = simulate_equity(
        simulate_once_fn=simulate_coinflip,
        target_ci=0.02,
        max_iter=5000,
        seed=999
    )
    
    # Same seed should produce identical results
    assert result1.p_hat == result2.p_hat, "Same seed should produce same p_hat"
    assert result1.n == result2.n, "Same seed should produce same sample count"
    assert result1.ci_radius == result2.ci_radius, "Same seed should produce same CI"
    
    # Different seed should produce different results (with high probability)
    result3 = simulate_equity(
        simulate_once_fn=simulate_coinflip,
        target_ci=0.02,
        max_iter=5000,
        seed=1000
    )
    
    # Different seeds should likely produce different results
    # (This could theoretically fail, but extremely unlikely)
    assert abs(result1.p_hat - result3.p_hat) > 0.001 or result1.n != result3.n, \
        "Different seeds should likely produce different results"


def test_ci_method_equivalence_smoke():
    """Test that both Wilson and normal CI methods produce reasonable intervals"""
    def simulate_fixed():
        # Fixed probability for deterministic testing
        import random
        win = random.random() < 0.3
        return win, False
    
    wilson_result = simulate_equity(
        simulate_once_fn=simulate_fixed,
        target_ci=0.02,
        max_iter=5000,
        seed=555,
        ci_method="wilson"
    )
    
    normal_result = simulate_equity(
        simulate_once_fn=simulate_fixed,
        target_ci=0.02,
        max_iter=5000,
        seed=555,
        ci_method="normal"
    )
    
    # Both methods should produce valid CIs
    assert 0 <= wilson_result.ci_low <= wilson_result.ci_high <= 1
    assert 0 <= normal_result.ci_low <= normal_result.ci_high <= 1
    
    # CI radius should be reasonable
    assert wilson_result.ci_radius <= 0.025, "Wilson CI radius should be reasonable"
    assert normal_result.ci_radius <= 0.025, "Normal CI radius should be reasonable"
    
    # p_hat should be the same (same seed, same simulations)
    assert wilson_result.p_hat == normal_result.p_hat, "p_hat should be identical"


def test_confidence_interval_functions():
    """Test CI calculation functions directly"""
    # Test Wilson CI
    ci_low, ci_high = wilson_confidence_interval(50, 100)
    assert 0 <= ci_low <= ci_high <= 1
    assert abs((ci_low + ci_high) / 2 - 0.5) < 0.1  # Should be roughly centered at 0.5
    
    # Test normal CI
    ci_low, ci_high = normal_confidence_interval(50, 100)
    assert 0 <= ci_low <= ci_high <= 1
    assert abs((ci_low + ci_high) / 2 - 0.5) < 0.1
    
    # Test edge cases
    ci_low, ci_high = wilson_confidence_interval(0, 0)
    assert ci_low == 0.0 and ci_high == 1.0  # No data case
    
    ci_low, ci_high = wilson_confidence_interval(0, 100)
    assert ci_low == 0.0 and ci_high > 0  # No wins but some data


def test_calculate_required_samples():
    """Test sample size calculation"""
    # For p=0.5 and ±1% CI, should need ~9,600 samples
    n_needed = calculate_required_samples(target_ci=0.01, p_estimate=0.5)
    assert 9000 <= n_needed <= 10000, f"Expected ~9,600 samples, got {n_needed}"
    
    # Smaller CI should need more samples
    n_small = calculate_required_samples(target_ci=0.005, p_estimate=0.5)
    n_large = calculate_required_samples(target_ci=0.02, p_estimate=0.5)
    assert n_small > n_large, "Smaller CI should require more samples"


def test_equity_result_to_dict():
    """Test EquityResult serialization"""
    result = EquityResult(
        p_hat=0.65,
        ci_low=0.60,
        ci_high=0.70,
        ci_radius=0.05,
        n=1000,
        stopped_early=True,
        mode="MC",
        seed=42,
        tie_probability=0.05,
        lose_probability=0.30
    )
    
    d = result.to_dict()
    assert d["win_probability"] == 0.65
    assert d["ci_radius"] == 0.05
    assert d["samples"] == 1000
    assert d["stopped_early"] is True
    assert d["seed"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])