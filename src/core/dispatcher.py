"""
Automatic dispatcher for choosing between enumeration and Monte Carlo
枚举和蒙特卡罗之间的自动调度器
"""

from typing import List, Optional, Union, Callable
import sys
from pathlib import Path

# Add parent directory to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import Card
from .equity_result import EquityResult
from .enumeration import PokerEnumerator
from .monte_carlo import simulate_equity


class EquityDispatcher:
    """
    Intelligent dispatcher that chooses between enumeration and Monte Carlo
    在枚举和蒙特卡罗之间智能选择的调度器
    """
    
    def __init__(self, use_fast_evaluator: bool = True):
        """Initialize dispatcher with evaluator preference"""
        self.enumerator = PokerEnumerator(use_fast_evaluator=use_fast_evaluator)
        self.use_fast_evaluator = use_fast_evaluator
    
    def compute_equity(
        self,
        hero_cards: List[Card],
        opponent_specs: List[Union[List[Card], str, None]],  # Cards, "random", or None
        community_cards: List[Card] = None,
        target_ci: float = 0.005,
        max_iter: int = 2_000_000,
        seed: Optional[int] = None,
        force_method: Optional[str] = None,  # "enum", "mc", or None for auto
        verbose: bool = False
    ) -> EquityResult:
        """
        Compute equity using the best available method
        使用最佳可用方法计算权益
        
        Args:
            hero_cards: Hero's hole cards
            opponent_specs: List of opponent specifications
                - List[Card]: Known opponent cards
                - "random" or None: Random opponent
            community_cards: Known community cards
            target_ci: Target confidence interval for MC
            max_iter: Maximum iterations for MC
            seed: Random seed for reproducibility
            force_method: Force specific method ("enum" or "mc")
            verbose: Print method selection reasoning
            
        Returns:
            EquityResult with appropriate method used
        """
        if community_cards is None:
            community_cards = []
        
        # Parse opponent specifications
        known_opponents = []
        num_random_opponents = 0
        
        for spec in opponent_specs:
            if spec is None or spec == "random":
                num_random_opponents += 1
                known_opponents.append(None)
            elif isinstance(spec, list) and len(spec) == 2:
                known_opponents.append(spec)
            else:
                raise ValueError(f"Invalid opponent specification: {spec}")
        
        num_total_opponents = len(opponent_specs)
        num_known_opponents = len([opp for opp in known_opponents if opp is not None])
        
        # Method selection logic
        if force_method == "enum":
            method = "enum"
            reason = "forced enumeration"
        elif force_method == "mc":
            method = "mc" 
            reason = "forced Monte Carlo"
        else:
            # Automatic selection
            should_enumerate = self.enumerator.should_use_enumeration(
                num_total_opponents=num_total_opponents,
                num_known_opponents=num_known_opponents,
                num_community_cards=len(community_cards)
            )
            
            if should_enumerate:
                method = "enum"
                reason = self._get_enumeration_reason(
                    num_total_opponents, num_known_opponents, len(community_cards)
                )
            else:
                method = "mc"
                reason = self._get_monte_carlo_reason(
                    num_total_opponents, num_known_opponents, len(community_cards)
                )
        
        if verbose:
            print(f"Method: {method.upper()} - {reason}")
        
        # Execute chosen method
        if method == "enum":
            return self._compute_enumeration(
                hero_cards, known_opponents, community_cards
            )
        else:
            return self._compute_monte_carlo(
                hero_cards, opponent_specs, community_cards,
                target_ci, max_iter, seed
            )
    
    def _compute_enumeration(
        self,
        hero_cards: List[Card],
        opponent_cards: List[Optional[List[Card]]],
        community_cards: List[Card]
    ) -> EquityResult:
        """Execute enumeration calculation"""
        try:
            return self.enumerator.enumerate_equity(
                hero_cards=hero_cards,
                opponent_cards=opponent_cards,
                community_cards=community_cards
            )
        except Exception as e:
            # Fallback to Monte Carlo if enumeration fails
            print(f"Enumeration failed ({e}), falling back to Monte Carlo")
            return self._compute_monte_carlo(
                hero_cards, 
                ["random"] * len(opponent_cards),  # Convert to random opponents
                community_cards,
                target_ci=0.01,  # Default CI for fallback
                max_iter=50_000,  # Reduced for fallback
                seed=None
            )
    
    def _compute_monte_carlo(
        self,
        hero_cards: List[Card],
        opponent_specs: List[Union[List[Card], str, None]],
        community_cards: List[Card],
        target_ci: float,
        max_iter: int,
        seed: Optional[int]
    ) -> EquityResult:
        """Execute Monte Carlo calculation"""
        # Create simulation function for Monte Carlo
        def simulate_once():
            # This is a simplified simulation function
            # In a full implementation, this would integrate with the actual card dealing
            import random
            from texas_holdem_calculator import TexasHoldemCalculator
            
            try:
                calculator = TexasHoldemCalculator(
                    use_fast_evaluator=self.use_fast_evaluator,
                    random_seed=None  # Don't set seed here, it's managed at higher level
                )
                
                # Count random opponents
                num_random = len([spec for spec in opponent_specs 
                                if spec is None or spec == "random"])
                
                # Run single simulation
                result = calculator.calculate_win_probability(
                    hole_cards=hero_cards,
                    community_cards=community_cards,
                    num_opponents=num_random,
                    num_simulations=1,
                    force_simulation=True
                )
                
                win_prob = result.get('win_probability', 0.0)
                tie_prob = result.get('tie_probability', 0.0)
                
                # Convert to binary outcome
                rand_val = random.random()
                if rand_val < win_prob:
                    return True, False  # Win
                elif rand_val < win_prob + tie_prob:
                    return False, True  # Tie
                else:
                    return False, False  # Lose
                    
            except Exception:
                return False, False
        
        return simulate_equity(
            simulate_once_fn=simulate_once,
            target_ci=target_ci,
            max_iter=max_iter,
            seed=seed,
            ci_method="wilson"
        )
    
    def _get_enumeration_reason(self, num_total: int, num_known: int, num_community: int) -> str:
        """Get human-readable reason for choosing enumeration"""
        reasons = []
        
        if num_total <= 2:
            reasons.append(f"≤2 opponents ({num_total})")
        
        if num_community >= 4:
            reasons.append(f"≥4 community cards ({num_community})")
        
        num_random = num_total - num_known
        if num_random <= 1:
            reasons.append(f"≤1 random opponent ({num_random})")
        
        if not reasons:
            reasons.append("small scenario space")
        
        return "exact enumeration feasible (" + ", ".join(reasons) + ")"
    
    def _get_monte_carlo_reason(self, num_total: int, num_known: int, num_community: int) -> str:
        """Get human-readable reason for choosing Monte Carlo"""
        reasons = []
        
        if num_total > 2:
            reasons.append(f">2 opponents ({num_total})")
        
        if num_community < 3:
            reasons.append(f"<3 community cards ({num_community})")
        
        num_random = num_total - num_known
        if num_random > 1:
            reasons.append(f">1 random opponent ({num_random})")
        
        if not reasons:
            reasons.append("large scenario space")
        
        return "Monte Carlo simulation required (" + ", ".join(reasons) + ")"


def compute_equity(
    hero_cards: List[Card],
    opponent_specs: List[Union[List[Card], str, None]],
    community_cards: List[Card] = None,
    target_ci: float = 0.005,
    max_iter: int = 2_000_000,
    seed: Optional[int] = None,
    auto: bool = True,
    force_method: Optional[str] = None,
    verbose: bool = False
) -> EquityResult:
    """
    Convenience function for automatic equity computation
    自动权益计算的便利函数
    """
    dispatcher = EquityDispatcher(use_fast_evaluator=True)
    
    # Use passed force_method, or auto-select if not specified
    if force_method is None and not auto:
        force_method = "mc"  # Default to MC if not auto and no force
    
    return dispatcher.compute_equity(
        hero_cards=hero_cards,
        opponent_specs=opponent_specs,
        community_cards=community_cards,
        target_ci=target_ci,
        max_iter=max_iter,
        seed=seed,
        force_method=force_method,
        verbose=verbose
    )