"""
Exact enumeration for heads-up and small scenarios
1v1和小场景的精确枚举计算

Features:
- Optimized 1v1 enumeration (preflop through river)
- Efficient 1v2 enumeration for turn/river
- Memory-efficient iterative calculation
- Exact probabilities with no sampling error
- Smart complexity estimation
"""

import math
from itertools import combinations
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import sys
from pathlib import Path

# Add parent directory to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import Card, HandEvaluator, FastHandEvaluator, Deck
from .equity_result import EquityResult


@dataclass
class EnumerationComplexity:
    """Analysis of enumeration computational complexity"""
    total_scenarios: int
    community_completions: int
    opponent_combinations: int
    is_feasible: bool
    estimated_time_ms: float
    memory_mb: float


class ExactEnumerator:
    """
    High-performance exact enumeration for poker scenarios
    扑克场景的高性能精确枚举
    """
    
    def __init__(self, use_fast_evaluator: bool = True):
        """
        Initialize with hand evaluator
        
        Args:
            use_fast_evaluator: Use FastHandEvaluator for better performance
        """
        self.hand_evaluator = FastHandEvaluator() if use_fast_evaluator else HandEvaluator()
        
        # Performance estimation constants (calibrated for typical hardware)
        self.evaluations_per_second = 1_000_000  # Hand evaluations per second
        self.bytes_per_scenario = 64  # Memory per scenario
    
    def enumerate_heads_up(
        self,
        hero_cards: List[Card],
        villain_cards: Optional[List[Card]] = None,
        community_cards: Optional[List[Card]] = None
    ) -> EquityResult:
        """
        Exact heads-up enumeration (hero vs 1 opponent)
        1v1精确枚举
        
        Args:
            hero_cards: Hero's hole cards (exactly 2)
            villain_cards: Villain's hole cards (2 if known, None for random)
            community_cards: Known community cards (0-5)
            
        Returns:
            EquityResult with exact probabilities
        """
        if len(hero_cards) != 2:
            raise ValueError("Hero must have exactly 2 hole cards")
        
        if villain_cards and len(villain_cards) != 2:
            raise ValueError("Villain must have exactly 2 hole cards if specified")
        
        community_cards = community_cards or []
        if len(community_cards) > 5:
            raise ValueError("Maximum 5 community cards allowed")
        
        # Check enumeration feasibility
        complexity = self._analyze_complexity(
            hero_cards=hero_cards,
            opponent_cards=[villain_cards] if villain_cards else [None],
            community_cards=community_cards
        )
        
        if not complexity.is_feasible:
            raise ValueError(f"Enumeration too complex: {complexity.total_scenarios:,} scenarios")
        
        # Set up deck and remove known cards
        deck = Deck()
        known_cards = hero_cards + community_cards
        if villain_cards:
            known_cards.extend(villain_cards)
        
        deck.remove_cards(known_cards)
        remaining_cards = deck.cards
        
        wins = 0
        ties = 0
        total_scenarios = 0
        
        # Calculate remaining community cards needed
        community_needed = 5 - len(community_cards)
        
        # Generate all possible community completions
        if community_needed > 0:
            community_completions = list(combinations(remaining_cards, community_needed))
        else:
            community_completions = [()]  # No additional community cards needed
        
        for community_completion in community_completions:
            complete_community = community_cards + list(community_completion)
            
            # Remove used community cards from villain options
            if villain_cards:
                # Villain cards are known - just evaluate this scenario
                villain_hole_combinations = [villain_cards]
            else:
                # Generate all possible villain hole cards
                available_for_villain = [
                    card for card in remaining_cards 
                    if card not in community_completion
                ]
                villain_hole_combinations = list(combinations(available_for_villain, 2))
            
            for villain_hole in villain_hole_combinations:
                total_scenarios += 1
                
                # Build complete hands
                hero_hand = hero_cards + complete_community
                villain_hand = list(villain_hole) + complete_community
                
                # Compare hands using fast evaluator
                if hasattr(self.hand_evaluator, 'compare_hands'):
                    comparison = self.hand_evaluator.compare_hands(hero_hand, villain_hand)
                else:
                    # Fallback comparison
                    hero_rank, hero_values = self.hand_evaluator.evaluate_hand(hero_hand)
                    villain_rank, villain_values = self.hand_evaluator.evaluate_hand(villain_hand)
                    
                    if hero_rank.value > villain_rank.value:
                        comparison = 1
                    elif hero_rank.value < villain_rank.value:
                        comparison = -1
                    elif hero_values > villain_values:
                        comparison = 1
                    elif hero_values < villain_values:
                        comparison = -1
                    else:
                        comparison = 0
                
                if comparison > 0:  # Hero wins
                    wins += 1
                elif comparison == 0:  # Tie
                    ties += 1
                # Hero loses: no increment needed
        
        # Calculate final probabilities
        if total_scenarios == 0:
            return EquityResult(
                p_hat=0.0, ci_low=0.0, ci_high=1.0, ci_radius=0.5,
                n=0, stopped_early=False, mode="EXACT_ENUM",
                tie_probability=0.0, lose_probability=1.0
            )
        
        win_prob = wins / total_scenarios
        tie_prob = ties / total_scenarios
        lose_prob = 1.0 - win_prob - tie_prob
        
        return EquityResult(
            p_hat=win_prob,
            ci_low=win_prob,  # Exact calculation - no uncertainty
            ci_high=win_prob,
            ci_radius=0.0,
            n=total_scenarios,
            stopped_early=False,
            mode="EXACT_ENUM",
            tie_probability=tie_prob,
            lose_probability=lose_prob
        )
    
    def enumerate_multiway(
        self,
        hero_cards: List[Card],
        opponent_cards: List[Optional[List[Card]]],
        community_cards: Optional[List[Card]] = None,
        max_scenarios: int = 100_000
    ) -> EquityResult:
        """
        Exact enumeration for multiway pots (hero vs 2+ opponents)
        多人底池的精确枚举
        
        Args:
            hero_cards: Hero's hole cards
            opponent_cards: List of opponent hole cards (None for unknown)
            community_cards: Known community cards
            max_scenarios: Maximum scenarios before falling back to MC
            
        Returns:
            EquityResult with exact probabilities or error
        """
        if len(hero_cards) != 2:
            raise ValueError("Hero must have exactly 2 hole cards")
        
        community_cards = community_cards or []
        
        # Validate opponent cards
        num_opponents = len(opponent_cards)
        known_opponents = [opp for opp in opponent_cards if opp is not None]
        num_random_opponents = len([opp for opp in opponent_cards if opp is None])
        
        for i, opp_cards in enumerate(known_opponents):
            if len(opp_cards) != 2:
                raise ValueError(f"Opponent {i} must have exactly 2 hole cards")
        
        # Check complexity
        complexity = self._analyze_complexity(hero_cards, opponent_cards, community_cards)
        
        if complexity.total_scenarios > max_scenarios:
            raise ValueError(
                f"Scenario too complex: {complexity.total_scenarios:,} > {max_scenarios:,}. "
                f"Use Monte Carlo simulation instead."
            )
        
        # Set up enumeration
        deck = Deck()
        all_known_cards = hero_cards + community_cards
        for opp_cards in known_opponents:
            all_known_cards.extend(opp_cards)
        
        deck.remove_cards(all_known_cards)
        remaining_cards = deck.cards
        
        wins = 0
        ties = 0
        total_scenarios = 0
        
        # Calculate remaining cards needed
        community_needed = 5 - len(community_cards)
        
        # Generate community completions
        if community_needed > 0:
            community_completions = list(combinations(remaining_cards, community_needed))
        else:
            community_completions = [()]
        
        for community_completion in community_completions:
            complete_community = community_cards + list(community_completion)
            
            # Available cards for random opponents
            available_for_opponents = [
                card for card in remaining_cards 
                if card not in community_completion
            ]
            
            # Generate random opponent combinations
            if num_random_opponents > 0:
                random_opponent_combos = self._generate_random_opponent_combinations(
                    available_for_opponents, num_random_opponents
                )
            else:
                random_opponent_combos = [[]]
            
            for random_opponent_combo in random_opponent_combos:
                total_scenarios += 1
                
                # Build all opponent hands
                all_opponent_hands = []
                
                # Add known opponents
                for opp_cards in known_opponents:
                    all_opponent_hands.append(opp_cards + complete_community)
                
                # Add random opponents
                for random_opp_cards in random_opponent_combo:
                    all_opponent_hands.append(list(random_opp_cards) + complete_community)
                
                # Evaluate hero hand
                hero_hand = hero_cards + complete_community
                
                # Check if hero wins against all opponents
                hero_wins = True
                tie_occurred = False
                
                for opponent_hand in all_opponent_hands:
                    if hasattr(self.hand_evaluator, 'compare_hands'):
                        comparison = self.hand_evaluator.compare_hands(hero_hand, opponent_hand)
                    else:
                        # Fallback comparison
                        hero_rank, hero_values = self.hand_evaluator.evaluate_hand(hero_hand)
                        opp_rank, opp_values = self.hand_evaluator.evaluate_hand(opponent_hand)
                        
                        if hero_rank.value > opp_rank.value:
                            comparison = 1
                        elif hero_rank.value < opp_rank.value:
                            comparison = -1
                        elif hero_values > opp_values:
                            comparison = 1
                        elif hero_values < opp_values:
                            comparison = -1
                        else:
                            comparison = 0
                    
                    if comparison < 0:  # Hero loses to this opponent
                        hero_wins = False
                        break
                    elif comparison == 0:  # Tie with this opponent
                        tie_occurred = True
                
                if hero_wins and not tie_occurred:
                    wins += 1
                elif hero_wins and tie_occurred:
                    ties += 1
        
        # Calculate results
        if total_scenarios == 0:
            return EquityResult(
                p_hat=0.0, ci_low=0.0, ci_high=1.0, ci_radius=0.5,
                n=0, stopped_early=False, mode="EXACT_ENUM",
                tie_probability=0.0, lose_probability=1.0
            )
        
        win_prob = wins / total_scenarios
        tie_prob = ties / total_scenarios
        lose_prob = 1.0 - win_prob - tie_prob
        
        return EquityResult(
            p_hat=win_prob,
            ci_low=win_prob,
            ci_high=win_prob,
            ci_radius=0.0,
            n=total_scenarios,
            stopped_early=False,
            mode="EXACT_ENUM",
            tie_probability=tie_prob,
            lose_probability=lose_prob
        )
    
    def _analyze_complexity(
        self,
        hero_cards: List[Card],
        opponent_cards: List[Optional[List[Card]]],
        community_cards: List[Card]
    ) -> EnumerationComplexity:
        """
        Analyze computational complexity of enumeration
        分析枚举的计算复杂度
        """
        num_opponents = len(opponent_cards)
        known_opponents = [opp for opp in opponent_cards if opp is not None]
        num_random_opponents = len([opp for opp in opponent_cards if opp is None])
        
        # Calculate remaining deck size
        total_known_cards = 2 + len(community_cards)  # Hero cards + community
        for opp_cards in known_opponents:
            total_known_cards += 2
        
        remaining_deck_size = 52 - total_known_cards
        community_needed = 5 - len(community_cards)
        
        # Calculate community completions
        if community_needed > 0 and remaining_deck_size >= community_needed:
            community_completions = math.comb(remaining_deck_size, community_needed)
        else:
            community_completions = 1
        
        # Calculate opponent combinations per community completion
        cards_left_after_community = remaining_deck_size - community_needed
        opponent_combinations = 1
        
        for opp in range(num_random_opponents):
            cards_available = cards_left_after_community - (2 * opp)
            if cards_available >= 2:
                this_opp_combos = math.comb(cards_available, 2)
                opponent_combinations *= this_opp_combos
            else:
                # Not enough cards available
                return EnumerationComplexity(
                    total_scenarios=0,
                    community_completions=0,
                    opponent_combinations=0,
                    is_feasible=False,
                    estimated_time_ms=float('inf'),
                    memory_mb=float('inf')
                )
        
        total_scenarios = community_completions * opponent_combinations
        
        # Estimate performance
        estimated_time_ms = (total_scenarios / self.evaluations_per_second) * 1000
        memory_mb = (total_scenarios * self.bytes_per_scenario) / (1024 * 1024)
        
        # Feasibility thresholds
        is_feasible = (
            total_scenarios <= 1_000_000 and  # Max scenarios
            estimated_time_ms <= 30_000 and   # Max 30 seconds
            memory_mb <= 100                  # Max 100 MB
        )
        
        return EnumerationComplexity(
            total_scenarios=total_scenarios,
            community_completions=community_completions,
            opponent_combinations=opponent_combinations,
            is_feasible=is_feasible,
            estimated_time_ms=estimated_time_ms,
            memory_mb=memory_mb
        )
    
    def _generate_random_opponent_combinations(
        self, available_cards: List[Card], num_opponents: int
    ) -> List[List[List[Card]]]:
        """
        Generate all possible combinations of random opponent hole cards
        生成所有可能的随机对手底牌组合
        """
        if num_opponents == 0:
            return [[]]
        
        if num_opponents == 1:
            return [[list(combo)] for combo in combinations(available_cards, 2)]
        
        # Multiple opponents: recursive generation with optimization
        all_combinations = []
        
        for first_opponent_cards in combinations(available_cards, 2):
            remaining_cards = [
                card for card in available_cards 
                if card not in first_opponent_cards
            ]
            
            remaining_opponent_combos = self._generate_random_opponent_combinations(
                remaining_cards, num_opponents - 1
            )
            
            for remaining_combo in remaining_opponent_combos:
                complete_combo = [list(first_opponent_cards)] + remaining_combo
                all_combinations.append(complete_combo)
        
        return all_combinations
    
    def should_use_enumeration(
        self,
        num_opponents: int,
        num_community_cards: int,
        known_opponents: int = 0,
        time_limit_ms: float = 10_000
    ) -> bool:
        """
        Determine if enumeration is recommended for given scenario
        判断给定场景是否推荐使用枚举
        
        Args:
            num_opponents: Total number of opponents
            num_community_cards: Number of known community cards
            known_opponents: Number of opponents with known cards
            time_limit_ms: Maximum acceptable computation time
            
        Returns:
            True if enumeration is recommended
        """
        # Quick checks for obviously unfeasible scenarios
        if num_opponents > 3:
            return False
        
        num_random_opponents = num_opponents - known_opponents
        if num_random_opponents > 2:
            return False
        
        # Estimate rough complexity
        remaining_community = 5 - num_community_cards
        
        # Conservative estimation
        remaining_deck_size = 52 - 2 - (2 * known_opponents) - num_community_cards
        
        if remaining_community > 0:
            community_combos = min(10_000, math.comb(remaining_deck_size, remaining_community))
        else:
            community_combos = 1
        
        # Estimate opponent combinations
        cards_for_opponents = remaining_deck_size - remaining_community
        if num_random_opponents == 1:
            opponent_combos = min(10_000, math.comb(cards_for_opponents, 2))
        elif num_random_opponents == 2:
            if cards_for_opponents >= 4:
                first_opp = math.comb(cards_for_opponents, 2)
                second_opp = math.comb(cards_for_opponents - 2, 2)
                opponent_combos = min(100_000, first_opp * second_opp)
            else:
                return False
        else:
            opponent_combos = 1
        
        total_scenarios = community_combos * opponent_combos
        estimated_time = (total_scenarios / self.evaluations_per_second) * 1000
        
        return estimated_time <= time_limit_ms and total_scenarios <= 500_000


# Convenience functions for backward compatibility
def enumerate_heads_up_equity(
    hero_cards: List[Card],
    villain_cards: Optional[List[Card]] = None,
    community_cards: Optional[List[Card]] = None
) -> EquityResult:
    """
    Convenience function for heads-up enumeration
    1v1枚举的便利函数
    """
    enumerator = ExactEnumerator(use_fast_evaluator=True)
    return enumerator.enumerate_heads_up(hero_cards, villain_cards, community_cards)


def should_use_enumeration(
    num_opponents: int,
    num_community_cards: int,
    known_opponents: int = 0
) -> bool:
    """
    Convenience function to check if enumeration is recommended
    检查是否推荐使用枚举的便利函数
    """
    enumerator = ExactEnumerator()
    return enumerator.should_use_enumeration(num_opponents, num_community_cards, known_opponents)