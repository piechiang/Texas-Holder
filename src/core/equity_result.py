"""
Equity calculation result data structures
权益计算结果数据结构
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EquityResult:
    """
    Result of equity calculation with confidence intervals and metadata
    包含置信区间和元数据的权益计算结果
    """
    p_hat: float  # Estimated win probability
    ci_low: float  # Lower bound of 95% confidence interval
    ci_high: float  # Upper bound of 95% confidence interval
    ci_radius: float  # Half-width of confidence interval
    n: int  # Number of samples/simulations
    stopped_early: bool  # Whether early stopping was triggered
    mode: str  # "MC" for Monte Carlo, "ENUM" for enumeration
    seed: Optional[int] = None  # Random seed used (if any)
    tie_probability: float = 0.0  # Probability of ties
    lose_probability: float = 0.0  # Probability of losing
    
    @property
    def win_probability(self) -> float:
        """Alias for p_hat for backward compatibility"""
        return self.p_hat
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "win_probability": self.p_hat,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "ci_radius": self.ci_radius,
            "samples": self.n,
            "stopped_early": self.stopped_early,
            "mode": self.mode,
            "seed": self.seed,
            "tie_probability": self.tie_probability,
            "lose_probability": self.lose_probability
        }