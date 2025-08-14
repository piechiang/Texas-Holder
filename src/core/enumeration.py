"""
Exact enumeration for small-scale poker scenarios
小规模扑克场景的精确枚举
"""

from itertools import combinations
from typing import List, Tuple, Optional
import sys
from pathlib import Path

# Add parent directory to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import Card, HandEvaluator, FastHandEvaluator, Deck
from .equity_result import EquityResult


class PokerEnumerator:
    """
    Exact enumeration calculator for poker equity
    扑克权益精确枚举计算器
    """
    
    def __init__(self, use_fast_evaluator: bool = True):
        """Initialize with hand evaluator"""
        self.hand_evaluator = FastHandEvaluator() if use_fast_evaluator else HandEvaluator()
    
    def enumerate_equity(
        self, 
        hero_cards: List[Card],
        opponent_cards: List[List[Card]],  # List of opponent hole cards, None for random
        community_cards: List[Card] = None,
        board_cards: List[Card] = None  # Alias for community_cards
    ) -> EquityResult:
        """
        Calculate exact equity using complete enumeration
        使用完全枚举计算精确权益
        
        Args:
            hero_cards: Hero's hole cards (exactly 2 cards)
            opponent_cards: List of opponent hole cards, None entries for random opponents
            community_cards: Known community cards (0-5 cards)
            board_cards: Alias for community_cards
            
        Returns:
            EquityResult with exact calculations
        """
        if community_cards is None:
            community_cards = board_cards or []
        
        if len(hero_cards) != 2:
            raise ValueError("Hero must have exactly 2 hole cards")
        
        # Filter out None opponents and count randoms
        known_opponents = [opp for opp in opponent_cards if opp is not None]
        num_random_opponents = len([opp for opp in opponent_cards if opp is None])
        
        # Validate known opponent cards
        for i, opp_cards in enumerate(known_opponents):
            if len(opp_cards) != 2:
                raise ValueError(f"Opponent {i} must have exactly 2 hole cards")
        
        # Create deck and remove known cards
        deck = Deck()
        all_known_cards = hero_cards + community_cards
        for opp_cards in known_opponents:
            all_known_cards.extend(opp_cards)
        
        deck.remove_cards(all_known_cards)
        remaining_cards = deck.cards
        
        # Calculate complexity and ensure it's manageable
        complexity = self._estimate_complexity(
            len(remaining_cards), 
            5 - len(community_cards),  # remaining community cards
            num_random_opponents
        )
        
        if complexity > 1_000_000:  # Conservative limit
            raise ValueError(f"Enumeration too complex: {complexity:,} combinations. Use Monte Carlo instead.")
        
        # Perform enumeration
        wins = 0
        ties = 0
        total_scenarios = 0
        
        # Generate all possible community card completions
        remaining_community = 5 - len(community_cards)
        if remaining_community > 0:
            community_completions = list(combinations(remaining_cards, remaining_community))
        else:
            community_completions = [()]  # No additional cards needed
        
        for community_completion in community_completions:
            complete_community = community_cards + list(community_completion)
            
            # Remove used community cards from available cards
            available_for_opponents = [
                card for card in remaining_cards 
                if card not in community_completion
            ]
            
            # Generate all possible random opponent combinations
            if num_random_opponents > 0:
                random_opponent_combos = self._generate_random_opponent_combinations(
                    available_for_opponents, num_random_opponents
                )
            else:
                random_opponent_combos = [[]]  # No random opponents
            
            for random_opponent_combo in random_opponent_combos:
                total_scenarios += 1
                
                # Combine known and random opponents
                all_opponent_hands = []
                for opp_cards in known_opponents:
                    all_opponent_hands.append(opp_cards + complete_community)
                
                for random_opp_cards in random_opponent_combo:
                    all_opponent_hands.append(random_opp_cards + complete_community)
                
                # Evaluate hero hand
                hero_hand = hero_cards + complete_community
                
                # Compare with all opponents
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
                    
                    if comparison < 0:  # Hero loses
                        hero_wins = False
                        break
                    elif comparison == 0:  # Tie
                        tie_occurred = True
                
                if hero_wins and not tie_occurred:
                    wins += 1
                elif hero_wins and tie_occurred:
                    ties += 1
        
        # Calculate final probabilities
        if total_scenarios == 0:
            return EquityResult(
                p_hat=0.0, ci_low=0.0, ci_high=1.0, ci_radius=0.5,
                n=0, stopped_early=False, mode="ENUM",
                tie_probability=0.0, lose_probability=1.0
            )
        
        win_prob = wins / total_scenarios
        tie_prob = ties / total_scenarios
        lose_prob = 1.0 - win_prob - tie_prob
        
        return EquityResult(
            p_hat=win_prob,
            ci_low=win_prob,  # Exact calculation, no uncertainty
            ci_high=win_prob,
            ci_radius=0.0,
            n=total_scenarios,
            stopped_early=False,
            mode="ENUM",
            tie_probability=tie_prob,
            lose_probability=lose_prob
        )
    
    def _estimate_complexity(self, deck_size: int, remaining_community: int, num_random_opponents: int) -> int:
        """
        Estimate computational complexity of enumeration
        估算枚举的计算复杂度
        """
        # If no random opponents, complexity is just community card combinations
        if num_random_opponents == 0:
            if remaining_community > 0:
                community_combos = 1
                for i in range(remaining_community):
                    community_combos *= (deck_size - i)
                for i in range(1, remaining_community + 1):
                    community_combos //= i
                return community_combos
            else:
                return 1  # All cards known, just one scenario
        
        # Community card combinations
        if remaining_community > 0:
            community_combos = 1
            for i in range(remaining_community):
                community_combos *= (deck_size - i)
            for i in range(1, remaining_community + 1):
                community_combos //= i
        else:
            community_combos = 1
        
        # Random opponent combinations (for each community completion)
        cards_left_after_community = deck_size - remaining_community
        opponent_combos = 1
        
        for opp in range(num_random_opponents):
            cards_for_this_opp = cards_left_after_community - (2 * opp)
            if cards_for_this_opp >= 2:
                this_opp_combos = (cards_for_this_opp * (cards_for_this_opp - 1)) // 2
                opponent_combos *= this_opp_combos
            else:
                return float('inf')  # Not enough cards
        
        return community_combos * opponent_combos
    
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
        
        # Multiple opponents: recursive generation
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
        num_total_opponents: int, 
        num_known_opponents: int,
        num_community_cards: int
    ) -> bool:
        """
        Decide whether enumeration is feasible for given scenario
        决定给定场景是否适合使用枚举
        
        Args:
            num_total_opponents: Total number of opponents
            num_known_opponents: Number of opponents with known cards
            num_community_cards: Number of known community cards
            
        Returns:
            True if enumeration is recommended, False otherwise
        """
        num_random_opponents = num_total_opponents - num_known_opponents
        remaining_community = 5 - num_community_cards
        
        # Quick acceptance for simple cases
        if num_random_opponents == 0:
            # All opponents known - should always use enumeration for small scenarios
            if num_total_opponents <= 2:
                return True
            # Even with 3 known opponents, if many community cards are known
            if num_total_opponents == 3 and num_community_cards >= 4:
                return True
        
        # Conservative limits based on computational feasibility
        if num_total_opponents > 3:
            return False  # Too many opponents
        
        if num_random_opponents > 2:
            return False  # Too many random opponents
        
        # Special cases for random opponents
        if num_random_opponents == 1:
            # Single random opponent - usually feasible
            if num_community_cards >= 3:  # Flop or later
                return True
            if num_total_opponents == 1:  # Heads-up vs random
                return True
        
        # Calculate remaining deck size (approximate)
        remaining_deck_size = 52 - 2 - (2 * num_known_opponents) - num_community_cards
        
        try:
            complexity = self._estimate_complexity(
                remaining_deck_size, remaining_community, num_random_opponents
            )
            return complexity <= 500_000  # More generous threshold
        except:
            return False


def enumerate_equity(
    hero_cards: List[Card],
    opponent_cards: List[Optional[List[Card]]],
    community_cards: List[Card] = None
) -> EquityResult:
    """
    Convenience function for exact enumeration
    精确枚举的便利函数
    """
    enumerator = PokerEnumerator(use_fast_evaluator=True)
    return enumerator.enumerate_equity(hero_cards, opponent_cards, community_cards)