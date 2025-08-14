"""
Monte Carlo simulation with confidence intervals and early stopping
包含置信区间和早停的蒙特卡罗模拟
"""

import math
from typing import Optional, List, Tuple, Callable
from .equity_result import EquityResult
from .rng import RNGManager


def wilson_confidence_interval(wins: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """
    Calculate Wilson score confidence interval for binomial proportion
    计算二项分布比例的 Wilson 评分置信区间
    
    Args:
        wins: Number of successes
        n: Total number of trials
        alpha: Significance level (0.05 for 95% CI)
    
    Returns:
        (lower_bound, upper_bound) tuple
    """
    if n == 0:
        return 0.0, 1.0
    
    z = 1.96  # For 95% CI (approximation)
    p_hat = wins / n
    
    denominator = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denominator
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n) / denominator
    
    return max(0.0, center - margin), min(1.0, center + margin)


def normal_confidence_interval(wins: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """
    Calculate normal approximation confidence interval for binomial proportion
    计算二项分布比例的正态近似置信区间
    
    Args:
        wins: Number of successes  
        n: Total number of trials
        alpha: Significance level (0.05 for 95% CI)
    
    Returns:
        (lower_bound, upper_bound) tuple
    """
    if n == 0:
        return 0.0, 1.0
    
    z = 1.96  # For 95% CI
    p_hat = wins / n
    margin = z * math.sqrt(p_hat * (1 - p_hat) / n)
    
    return max(0.0, p_hat - margin), min(1.0, p_hat + margin)


def simulate_equity(
    simulate_once_fn: Callable[[], Tuple[bool, bool]],  # Returns (win, tie)
    target_ci: float = 0.005,
    max_iter: int = 2_000_000,
    seed: Optional[int] = None,
    ci_method: str = "wilson",
    check_interval: int = 1000
) -> EquityResult:
    """
    Monte Carlo simulation with confidence intervals and early stopping
    包含置信区间和早停的蒙特卡罗模拟
    
    Args:
        simulate_once_fn: Function that simulates one hand and returns (win, tie)
        target_ci: Target confidence interval half-width (e.g., 0.005 for ±0.5%)
        max_iter: Maximum number of iterations
        seed: Random seed for reproducibility
        ci_method: "wilson" or "normal" for CI calculation
        check_interval: Check early stopping condition every N iterations
    
    Returns:
        EquityResult with statistics and CI information
    """
    # Set seed for both numpy and Python random for reproducibility
    if seed is not None:
        import random
        import numpy as np
        random.seed(seed)
        np.random.seed(seed)
    
    rng = RNGManager(seed)
    
    wins = 0
    ties = 0
    n = 0
    stopped_early = False
    
    ci_calc = wilson_confidence_interval if ci_method == "wilson" else normal_confidence_interval
    
    while n < max_iter:
        # Run a batch of simulations
        batch_size = min(check_interval, max_iter - n)
        
        for _ in range(batch_size):
            win, tie = simulate_once_fn()
            if win:
                wins += 1
            elif tie:
                ties += 1
            n += 1
        
        # Check early stopping condition
        if n >= 100:  # Don't stop too early
            ci_low, ci_high = ci_calc(wins, n)
            ci_radius = (ci_high - ci_low) / 2
            
            if ci_radius <= target_ci:
                stopped_early = True
                break
    
    # Final calculations
    p_hat = wins / n if n > 0 else 0.0
    tie_prob = ties / n if n > 0 else 0.0
    lose_prob = 1.0 - p_hat - tie_prob
    
    if n > 0:
        ci_low, ci_high = ci_calc(wins, n)
        ci_radius = (ci_high - ci_low) / 2
    else:
        ci_low = ci_high = ci_radius = 0.0
    
    return EquityResult(
        p_hat=p_hat,
        ci_low=ci_low,
        ci_high=ci_high,
        ci_radius=ci_radius,
        n=n,
        stopped_early=stopped_early,
        mode="MC",
        seed=seed,
        tie_probability=tie_prob,
        lose_probability=lose_prob
    )


def calculate_required_samples(target_ci: float = 0.005, p_estimate: float = 0.5) -> int:
    """
    Calculate approximate number of samples needed for target CI width
    计算达到目标置信区间宽度所需的大概样本数
    
    Args:
        target_ci: Target confidence interval half-width
        p_estimate: Rough estimate of win probability (0.5 is most conservative)
    
    Returns:
        Estimated number of samples needed
    """
    z = 1.96  # For 95% CI
    # Using normal approximation: margin = z * sqrt(p*(1-p)/n)
    # Solving for n: n = (z^2 * p * (1-p)) / margin^2
    
    n_estimate = (z**2 * p_estimate * (1 - p_estimate)) / (target_ci**2)
    return int(math.ceil(n_estimate))