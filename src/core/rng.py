"""
Unified random number generator management
统一随机数生成器管理
"""

import numpy as np
from typing import Optional


class RNGManager:
    """
    Centralized random number generator for reproducible results
    集中式随机数生成器，用于可重现的结果
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def random(self) -> float:
        """Generate random float in [0, 1)"""
        return self.rng.random()
    
    def choice(self, a, size=None, replace=True, p=None):
        """Generate random choice from array"""
        return self.rng.choice(a, size=size, replace=replace, p=p)
    
    def shuffle(self, x):
        """Shuffle array in-place"""
        self.rng.shuffle(x)
        return x
    
    def integers(self, low, high=None, size=None):
        """Generate random integers"""
        return self.rng.integers(low, high, size=size)
    
    def reset_seed(self, seed: Optional[int] = None):
        """Reset RNG with new seed"""
        self.seed = seed
        self.rng = np.random.default_rng(seed)


# Global instance for backward compatibility
_global_rng = RNGManager()


def set_global_seed(seed: Optional[int] = None):
    """Set seed for global RNG instance"""
    global _global_rng
    _global_rng.reset_seed(seed)


def get_global_rng() -> RNGManager:
    """Get global RNG instance"""
    return _global_rng