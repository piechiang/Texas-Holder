"""
Enhanced Texas Hold'em Calculator with improved performance and features
增强版德州扑克计算器，性能更佳，功能更多

Features:
- Automatic method selection (enumeration vs Monte Carlo vs vectorized)
- Confidence intervals with Wilson score
- Reproducible results with seed control
- Performance monitoring and optimization
- Backward compatibility with original interface
"""

import random
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import sys
from pathlib import Path

# Add parent directory to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import Card, TexasHoldemCalculator, parse_card_string
from .equity_result import EquityResult
from .exact_enumeration import ExactEnumerator, should_use_enumeration
from .vectorized_monte_carlo import simulate_equity_vectorized
from .monte_carlo import simulate_equity
from .numba_evaluator import create_best_evaluator


@dataclass
class CalculationResult:
    """Enhanced result with detailed statistics and confidence intervals"""
    win_probability: float
    tie_probability: float
    lose_probability: float
    confidence_interval: Tuple[float, float]
    ci_radius: float
    simulations: int
    method: str
    stopped_early: bool
    seed: Optional[int]
    calculation_time_ms: float
    performance_stats: Dict[str, Any]


@dataclass
class CalculatorConfig:
    """Configuration for enhanced calculator"""
    # Method selection
    prefer_enumeration: bool = True
    prefer_vectorized: bool = True
    max_enumeration_time_ms: float = 10_000
    max_enumeration_scenarios: int = 500_000
    
    # Monte Carlo settings
    default_simulations: int = 10_000
    target_ci_radius: float = 0.005  # ±0.5%
    max_simulations: int = 2_000_000
    chunk_size: int = 10_000
    
    # Performance
    use_fast_evaluator: bool = True
    enable_caching: bool = True
    
    # Reproducibility
    default_seed: Optional[int] = None


class EnhancedTexasHoldemCalculator:
    """
    Enhanced Texas Hold'em calculator with automatic optimization
    增强版德州扑克计算器，具有自动优化功能
    """
    
    def __init__(self, config: Optional[CalculatorConfig] = None):
        """
        Initialize enhanced calculator
        
        Args:
            config: Configuration object for calculator behavior
        """
        self.config = config or CalculatorConfig()
        
        # Initialize components
        self.hand_evaluator = create_best_evaluator()
        self.exact_enumerator = ExactEnumerator(use_fast_evaluator=True)
        
        # Performance tracking
        self.performance_stats = {
            'total_calculations': 0,
            'enumeration_used': 0,
            'vectorized_mc_used': 0,
            'standard_mc_used': 0,
            'total_time_ms': 0.0,
            'average_time_ms': 0.0
        }
        
        # Backward compatibility
        self.original_calculator = TexasHoldemCalculator(
            use_fast_evaluator=self.config.use_fast_evaluator,
            random_seed=self.config.default_seed
        )
    
    def calculate_win_probability(
        self,
        hole_cards: List[Card],
        community_cards: Optional[List[Card]] = None,
        num_opponents: int = 1,
        num_simulations: Optional[int] = None,
        seed: Optional[int] = None,
        force_method: Optional[str] = None,
        target_ci: Optional[float] = None
    ) -> CalculationResult:
        """
        Calculate win probability with automatic method selection
        自动方法选择的胜率计算
        
        Args:
            hole_cards: Hero's hole cards
            community_cards: Known community cards
            num_opponents: Number of opponents
            num_simulations: Number of simulations (if using MC)
            seed: Random seed for reproducibility
            force_method: Force specific method ('enumeration', 'vectorized', 'standard')
            target_ci: Target confidence interval radius
            
        Returns:
            CalculationResult with detailed statistics
        """
        start_time = time.time()
        
        # Set defaults
        community_cards = community_cards or []
        num_simulations = num_simulations or self.config.default_simulations
        seed = seed or self.config.default_seed
        target_ci = target_ci or self.config.target_ci_radius
        
        # Validate inputs
        if len(hole_cards) != 2:
            raise ValueError("Hero must have exactly 2 hole cards")
        if len(community_cards) > 5:
            raise ValueError("Maximum 5 community cards allowed")
        
        # Set seed for reproducibility
        if seed is not None:
            random.seed(seed)
        
        # Determine calculation method
        method = self._select_method(
            num_opponents=num_opponents,
            num_community_cards=len(community_cards),
            force_method=force_method
        )
        
        # Perform calculation
        try:
            if method == 'enumeration':
                result = self._calculate_exact(hole_cards, community_cards, num_opponents)
            elif method == 'vectorized':
                result = self._calculate_vectorized(
                    hole_cards, community_cards, num_opponents, 
                    num_simulations, seed, target_ci
                )
            else:  # standard Monte Carlo
                result = self._calculate_standard_mc(
                    hole_cards, community_cards, num_opponents,
                    num_simulations, seed, target_ci
                )
        except Exception as e:
            # Fallback to standard Monte Carlo on any error
            result = self._calculate_standard_mc(
                hole_cards, community_cards, num_opponents,
                num_simulations, seed, target_ci
            )
            method = 'standard_fallback'
        
        # Calculate timing
        end_time = time.time()
        calculation_time_ms = (end_time - start_time) * 1000
        
        # Update performance stats
        self._update_performance_stats(method, calculation_time_ms)
        
        # Create enhanced result
        enhanced_result = CalculationResult(
            win_probability=result.p_hat,
            tie_probability=result.tie_probability,
            lose_probability=result.lose_probability,
            confidence_interval=(result.ci_low, result.ci_high),
            ci_radius=result.ci_radius,
            simulations=result.n,
            method=method,
            stopped_early=result.stopped_early,
            seed=seed,
            calculation_time_ms=calculation_time_ms,
            performance_stats=dict(self.performance_stats)
        )
        
        return enhanced_result
    
    def _select_method(
        self,
        num_opponents: int,
        num_community_cards: int,
        force_method: Optional[str]
    ) -> str:
        """
        Automatically select the best calculation method
        自动选择最佳计算方法
        """
        if force_method:
            return force_method
        
        # Check if enumeration is feasible and preferred
        if self.config.prefer_enumeration and self.exact_enumerator.should_use_enumeration(
            num_opponents=num_opponents,
            num_community_cards=num_community_cards,
            time_limit_ms=self.config.max_enumeration_time_ms
        ):
            return 'enumeration'
        
        # Use vectorized Monte Carlo if available and preferred
        if self.config.prefer_vectorized:
            try:
                import numpy as np
                return 'vectorized'
            except ImportError:
                pass
        
        # Default to standard Monte Carlo
        return 'standard'
    
    def _calculate_exact(
        self,
        hole_cards: List[Card],
        community_cards: List[Card],
        num_opponents: int
    ) -> EquityResult:
        """Calculate using exact enumeration"""
        if num_opponents == 1:
            return self.exact_enumerator.enumerate_heads_up(
                hero_cards=hole_cards,
                villain_cards=None,
                community_cards=community_cards
            )
        else:
            # For multiway, create opponent list with None for unknown opponents
            opponent_cards = [None] * num_opponents
            return self.exact_enumerator.enumerate_multiway(
                hero_cards=hole_cards,
                opponent_cards=opponent_cards,
                community_cards=community_cards,
                max_scenarios=self.config.max_enumeration_scenarios
            )
    
    def _calculate_vectorized(
        self,
        hole_cards: List[Card],
        community_cards: List[Card],
        num_opponents: int,
        num_simulations: int,
        seed: Optional[int],
        target_ci: float
    ) -> EquityResult:
        """Calculate using vectorized Monte Carlo"""
        return simulate_equity_vectorized(
            hero_cards=hole_cards,
            community_cards=community_cards,
            num_opponents=num_opponents,
            num_simulations=num_simulations,
            seed=seed,
            target_ci=target_ci,
            chunk_size=self.config.chunk_size
        )
    
    def _calculate_standard_mc(
        self,
        hole_cards: List[Card],
        community_cards: List[Card],
        num_opponents: int,
        num_simulations: int,
        seed: Optional[int],
        target_ci: float
    ) -> EquityResult:
        """Calculate using standard Monte Carlo"""
        # Create simulation function for the standard MC interface
        def simulate_once():
            # Use original calculator for one simulation
            result = self.original_calculator.calculate_win_probability(
                hole_cards=hole_cards,
                community_cards=community_cards,
                num_opponents=num_opponents,
                num_simulations=1,
                seed=None  # Don't set seed for individual simulations
            )
            
            # Determine if hero won or tied
            win = result['win_probability'] > 0.99  # Hero won this simulation
            tie = 0.01 < result['win_probability'] < 0.99  # Approximation for ties
            return win, tie
        
        return simulate_equity(
            simulate_once_fn=simulate_once,
            target_ci=target_ci,
            max_iter=num_simulations,
            seed=seed
        )
    
    def _update_performance_stats(self, method: str, calculation_time_ms: float):
        """Update performance tracking statistics"""
        self.performance_stats['total_calculations'] += 1
        self.performance_stats['total_time_ms'] += calculation_time_ms
        
        if method == 'enumeration':
            self.performance_stats['enumeration_used'] += 1
        elif method == 'vectorized':
            self.performance_stats['vectorized_mc_used'] += 1
        else:
            self.performance_stats['standard_mc_used'] += 1
        
        # Update average
        self.performance_stats['average_time_ms'] = (
            self.performance_stats['total_time_ms'] / 
            self.performance_stats['total_calculations']
        )
    
    def get_hand_strength(self, hole_cards: List[Card], community_cards: Optional[List[Card]] = None) -> Dict[str, Any]:
        """Get hand strength using enhanced evaluator"""
        return self.original_calculator.get_hand_strength(hole_cards, community_cards)
    
    def get_betting_recommendation(self, **kwargs) -> Dict[str, Any]:
        """Get betting recommendation using original logic"""
        return self.original_calculator.get_betting_recommendation(**kwargs)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics"""
        stats = dict(self.performance_stats)
        
        # Add percentages
        total = stats['total_calculations']
        if total > 0:
            stats['enumeration_percentage'] = (stats['enumeration_used'] / total) * 100
            stats['vectorized_percentage'] = (stats['vectorized_mc_used'] / total) * 100
            stats['standard_percentage'] = (stats['standard_mc_used'] / total) * 100
        
        # Add evaluator info
        stats['hand_evaluator'] = self.hand_evaluator.get_performance_info() if hasattr(
            self.hand_evaluator, 'get_performance_info'
        ) else {'type': 'standard'}
        
        return stats
    
    def reset_performance_stats(self):
        """Reset performance tracking statistics"""
        self.performance_stats = {
            'total_calculations': 0,
            'enumeration_used': 0,
            'vectorized_mc_used': 0,
            'standard_mc_used': 0,
            'total_time_ms': 0.0,
            'average_time_ms': 0.0
        }
    
    def benchmark(self, scenarios: List[Dict[str, Any]], include_methods: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Benchmark different calculation methods on given scenarios
        在给定场景上基准测试不同的计算方法
        
        Args:
            scenarios: List of scenario dicts with 'hole_cards', 'community_cards', 'num_opponents'
            include_methods: Methods to test ['enumeration', 'vectorized', 'standard']
            
        Returns:
            Benchmark results with timing and accuracy comparisons
        """
        include_methods = include_methods or ['enumeration', 'vectorized', 'standard']
        
        results = {}
        
        for method in include_methods:
            method_results = []
            total_time = 0.0
            
            for scenario in scenarios:
                try:
                    start_time = time.time()
                    result = self.calculate_win_probability(
                        hole_cards=scenario['hole_cards'],
                        community_cards=scenario.get('community_cards', []),
                        num_opponents=scenario.get('num_opponents', 1),
                        force_method=method,
                        seed=42  # Fixed seed for comparison
                    )
                    end_time = time.time()
                    
                    method_results.append({
                        'win_probability': result.win_probability,
                        'ci_radius': result.ci_radius,
                        'simulations': result.simulations,
                        'time_ms': (end_time - start_time) * 1000
                    })
                    total_time += (end_time - start_time) * 1000
                    
                except Exception as e:
                    method_results.append({
                        'error': str(e),
                        'time_ms': 0.0
                    })
            
            results[method] = {
                'results': method_results,
                'total_time_ms': total_time,
                'average_time_ms': total_time / len(scenarios) if scenarios else 0.0,
                'scenarios_completed': len([r for r in method_results if 'error' not in r])
            }
        
        return results


# Convenience functions for backward compatibility
def create_enhanced_calculator(
    prefer_enumeration: bool = True,
    prefer_vectorized: bool = True,
    default_simulations: int = 10_000,
    target_ci_radius: float = 0.005
) -> EnhancedTexasHoldemCalculator:
    """
    Create enhanced calculator with custom settings
    创建具有自定义设置的增强计算器
    """
    config = CalculatorConfig(
        prefer_enumeration=prefer_enumeration,
        prefer_vectorized=prefer_vectorized,
        default_simulations=default_simulations,
        target_ci_radius=target_ci_radius
    )
    return EnhancedTexasHoldemCalculator(config)


def calculate_with_confidence_intervals(
    hole_cards_str: str,
    community_cards_str: str = "",
    num_opponents: int = 1,
    target_ci: float = 0.005,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function for calculating with confidence intervals
    计算置信区间的便利函数
    
    Args:
        hole_cards_str: Hero's cards like "As Kh"
        community_cards_str: Community cards like "2c 3h 4s"
        num_opponents: Number of opponents
        target_ci: Target confidence interval radius
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with win probability and confidence interval
    """
    # Parse cards
    hole_cards = [parse_card_string(card) for card in hole_cards_str.split()]
    community_cards = [parse_card_string(card) for card in community_cards_str.split()] if community_cards_str else []
    
    # Create calculator
    calculator = create_enhanced_calculator(target_ci_radius=target_ci)
    
    # Calculate
    result = calculator.calculate_win_probability(
        hole_cards=hole_cards,
        community_cards=community_cards,
        num_opponents=num_opponents,
        seed=seed,
        target_ci=target_ci
    )
    
    return asdict(result)