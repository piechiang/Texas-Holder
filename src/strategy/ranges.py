"""
Advanced poker range parser with weights and blocker-aware sampling
高级扑克范围解析器，支持权重和阻断牌抽样
"""

import re
import random
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from itertools import combinations
import sys
from pathlib import Path

# Add parent directory to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import Card, Rank, Suit, parse_card_string


@dataclass
class Combo:
    """A specific two-card combination with weight"""
    cards: Tuple[Card, Card]
    weight: float = 1.0
    
    def __post_init__(self):
        # Ensure weight is between 0 and 1
        self.weight = max(0.0, min(1.0, self.weight))
    
    def __str__(self):
        return f"{self.cards[0]}{self.cards[1]}@{self.weight:.0%}"
    
    def __hash__(self):
        return hash((self.cards[0], self.cards[1]))
    
    def __eq__(self, other):
        if not isinstance(other, Combo):
            return False
        return self.cards == other.cards


@dataclass
class RangeHand:
    """A poker hand specification like AKs, QQ+, etc."""
    rank1: str  # A, K, Q, etc.
    rank2: str  # A, K, Q, etc.
    suited: Optional[bool] = None  # True=suited, False=offsuit, None=both
    
    def __str__(self):
        suffix = ""
        if self.suited is True:
            suffix = "s"
        elif self.suited is False:
            suffix = "o"
        return f"{self.rank1}{self.rank2}{suffix}"


class RangeParser:
    """
    Advanced range parser supporting the syntax:
    - JJ+, ATs+, KQo
    - 54s-76s (range)  
    - A5s@30% (explicit weight)
    - Comma-separated and merged
    
    支持高级范围语法的解析器
    """
    
    # Rank values for comparison
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
        'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    # Reverse mapping
    VALUE_RANKS = {v: k for k, v in RANK_VALUES.items()}
    
    def __init__(self):
        self.all_cards = self._generate_all_cards()
    
    def _generate_all_cards(self) -> List[Card]:
        """Generate all 52 cards"""
        cards = []
        for rank in Rank:
            for suit in Suit:
                cards.append(Card(rank, suit))
        return cards
    
    def parse_range(self, range_expr: str) -> List[Combo]:
        """
        Parse range expression into list of Combo objects
        解析范围表达式为组合列表
        
        Args:
            range_expr: Range like "JJ+, ATs+, KQo, 54s-76s, A5s@30%"
            
        Returns:
            List of Combo objects with weights
        """
        if not range_expr.strip():
            return []
        
        # Split by comma and process each part
        parts = [part.strip() for part in range_expr.split(',')]
        all_combos = []
        
        for part in parts:
            if not part:
                continue
            try:
                combos = self._parse_single_part(part)
                all_combos.extend(combos)
            except Exception as e:
                print(f"Warning: Could not parse '{part}': {e}")
                continue
        
        # Merge duplicates by combining weights
        return self._merge_combos(all_combos)
    
    def _parse_single_part(self, part: str) -> List[Combo]:
        """Parse a single part like 'AKs', 'QQ+', 'A5s@30%', '54s-76s'"""
        part = part.strip().upper()
        
        # Check for explicit weight (@XX%)
        weight = 1.0
        if '@' in part:
            hand_part, weight_part = part.split('@', 1)
            weight = self._parse_weight(weight_part)
            part = hand_part
        
        # Check for range indicators
        if '+' in part:
            return self._parse_plus_range(part, weight)
        elif '-' in part and len(part) > 3:  # Avoid single dash in card names
            return self._parse_dash_range(part, weight)
        else:
            return self._parse_exact_hand(part, weight)
    
    def _parse_weight(self, weight_str: str) -> float:
        """Parse weight string like '30%', '0.3', '50'"""
        weight_str = weight_str.strip()
        
        if weight_str.endswith('%'):
            return float(weight_str[:-1]) / 100.0
        else:
            value = float(weight_str)
            if value > 1.0:
                return value / 100.0  # Assume percentage
            return value
    
    def _parse_exact_hand(self, hand: str, weight: float) -> List[Combo]:
        """Parse exact hand like 'AKs', 'QQ', 'T9o'"""
        if len(hand) < 2:
            raise ValueError(f"Invalid hand format: {hand}")
        
        rank1, rank2 = hand[0], hand[1]
        
        # Determine if suited/offsuit specified
        suited = None
        if len(hand) >= 3:
            if hand[2].upper() == 'S':
                suited = True
            elif hand[2].upper() == 'O':
                suited = False
        
        return self._generate_combos(rank1, rank2, suited, weight)
    
    def _parse_plus_range(self, range_str: str, weight: float) -> List[Combo]:
        """Parse plus range like 'QQ+', 'ATs+'"""
        if not range_str.endswith('+'):
            raise ValueError(f"Invalid plus range: {range_str}")
        
        base_hand = range_str[:-1]
        rank1, rank2 = base_hand[0], base_hand[1]
        
        # Determine suited/offsuit
        suited = None
        if len(base_hand) >= 3:
            if base_hand[2].upper() == 'S':
                suited = True
            elif base_hand[2].upper() == 'O':
                suited = False
        
        combos = []
        
        if rank1 == rank2:  # Pocket pairs like QQ+
            start_value = self.RANK_VALUES[rank1]
            for value in range(start_value, 15):  # Up to AA
                rank = self.VALUE_RANKS[value]
                combos.extend(self._generate_combos(rank, rank, None, weight))
        else:  # Non-pairs like ATs+
            rank1_value = self.RANK_VALUES[rank1]
            start_value = self.RANK_VALUES[rank2]
            
            for value in range(start_value, rank1_value):  # rank2 up to (but not including) rank1
                rank = self.VALUE_RANKS[value]
                combos.extend(self._generate_combos(rank1, rank, suited, weight))
        
        return combos
    
    def _parse_dash_range(self, range_str: str, weight: float) -> List[Combo]:
        """Parse dash range like '54s-76s', 'KJ-KT'"""
        parts = range_str.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid dash range: {range_str}")
        
        start_hand, end_hand = parts[0].strip(), parts[1].strip()
        
        # Parse start and end hands
        start_rank1, start_rank2 = start_hand[0], start_hand[1]
        end_rank1, end_rank2 = end_hand[0], end_hand[1]
        
        # Determine suited/offsuit from end hand (more specific)
        suited = None
        if len(end_hand) >= 3:
            if end_hand[2].upper() == 'S':
                suited = True
            elif end_hand[2].upper() == 'O':
                suited = False
        
        # Generate range - for connectors like 54s-76s
        combos = []
        
        # Check if this is a connector-style range (different ranks)
        if start_rank1 != start_rank2 and end_rank1 != end_rank2:
            # For connectors like 54s-76s, generate consecutive pairs
            start_low = self.RANK_VALUES[start_rank2]  # 4 in 54s
            end_low = self.RANK_VALUES[end_rank2]      # 6 in 76s
            
            if start_low > end_low:
                start_low, end_low = end_low, start_low
            
            for low_value in range(start_low, end_low + 1):
                high_value = low_value + 1
                if high_value <= 14:  # Don't exceed Ace
                    low_rank = self.VALUE_RANKS[low_value]
                    high_rank = self.VALUE_RANKS[high_value]
                    combos.extend(self._generate_combos(high_rank, low_rank, suited, weight))
        else:
            # For same-rank ranges like KJ-KT, vary the second rank
            start_value = self.RANK_VALUES[start_rank2]
            end_value = self.RANK_VALUES[end_rank2]
            
            if start_value > end_value:
                start_value, end_value = end_value, start_value
            
            for value in range(start_value, end_value + 1):
                rank = self.VALUE_RANKS[value]
                combos.extend(self._generate_combos(start_rank1, rank, suited, weight))
        
        return combos
    
    def _generate_combos(self, rank1: str, rank2: str, suited: Optional[bool], weight: float) -> List[Combo]:
        """Generate all card combinations for given ranks and suited preference"""
        combos = []
        
        # Get all cards for each rank
        rank1_cards = [card for card in self.all_cards if self._card_rank_str(card) == rank1]
        rank2_cards = [card for card in self.all_cards if self._card_rank_str(card) == rank2]
        
        if rank1 == rank2:  # Pocket pairs
            for i, card1 in enumerate(rank1_cards):
                for card2 in rank1_cards[i+1:]:
                    combos.append(Combo((card1, card2), weight))
        else:  # Different ranks
            for card1 in rank1_cards:
                for card2 in rank2_cards:
                    is_suited = (card1.suit == card2.suit)
                    
                    if suited is None or suited == is_suited:
                        combos.append(Combo((card1, card2), weight))
        
        return combos
    
    def _card_rank_str(self, card: Card) -> str:
        """Convert card rank to string"""
        return {
            Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5',
            Rank.SIX: '6', Rank.SEVEN: '7', Rank.EIGHT: '8', Rank.NINE: '9',
            Rank.TEN: 'T', Rank.JACK: 'J', Rank.QUEEN: 'Q', Rank.KING: 'K', Rank.ACE: 'A'
        }[card.rank]
    
    def _merge_combos(self, combos: List[Combo]) -> List[Combo]:
        """Merge duplicate combos by combining weights"""
        combo_map = {}
        
        for combo in combos:
            # Use normalized card tuple as key
            key = self._normalize_cards(combo.cards)
            
            if key in combo_map:
                # Combine weights (but cap at 1.0)
                existing_weight = combo_map[key].weight
                new_weight = min(1.0, existing_weight + combo.weight)
                combo_map[key].weight = new_weight
            else:
                combo_map[key] = combo
        
        return list(combo_map.values())
    
    def _normalize_cards(self, cards: Tuple[Card, Card]) -> Tuple[tuple, tuple]:
        """Normalize card pair for deduplication"""
        card1 = (cards[0].rank.value, cards[0].suit.value)
        card2 = (cards[1].rank.value, cards[1].suit.value)
        
        # Sort to ensure consistent ordering
        if card1 > card2:
            card1, card2 = card2, card1
        
        return (card1, card2)


class WeightedRangeSampler:
    """
    Weighted range sampler with blocker-aware sampling
    支持权重和阻断牌的范围抽样器
    """
    
    def __init__(self, combos: List[Combo], rng: Optional[random.Random] = None):
        """
        Initialize sampler with weighted combos
        
        Args:
            combos: List of Combo objects with weights
            rng: Optional random number generator for reproducibility
        """
        self.combos = combos
        self.rng = rng or random.Random()
        
        # Normalize weights to create probability distribution
        total_weight = sum(combo.weight for combo in combos)
        if total_weight == 0:
            self.probabilities = [1.0 / len(combos)] * len(combos)
        else:
            self.probabilities = [combo.weight / total_weight for combo in combos]
    
    def sample(self, blocked_cards: Optional[List[Card]] = None) -> Optional[Combo]:
        """
        Sample a combo respecting blockers
        抽样一个组合，尊重阻断牌
        
        Args:
            blocked_cards: Cards that cannot be used (already dealt)
            
        Returns:
            Sampled Combo or None if no valid combos available
        """
        if not self.combos:
            return None
        
        blocked_set = set(blocked_cards) if blocked_cards else set()
        
        # Filter valid combos (no conflicts with blocked cards)
        valid_indices = []
        valid_probs = []
        
        for i, combo in enumerate(self.combos):
            if not any(card in blocked_set for card in combo.cards):
                valid_indices.append(i)
                valid_probs.append(self.probabilities[i])
        
        if not valid_indices:
            return None
        
        # Renormalize probabilities
        total_prob = sum(valid_probs)
        if total_prob == 0:
            # Equal probability fallback
            valid_probs = [1.0 / len(valid_indices)] * len(valid_indices)
        else:
            valid_probs = [p / total_prob for p in valid_probs]
        
        # Sample using cumulative distribution
        rand_val = self.rng.random()
        cumulative = 0.0
        
        for i, prob in enumerate(valid_probs):
            cumulative += prob
            if rand_val <= cumulative:
                return self.combos[valid_indices[i]]
        
        # Fallback to last valid combo
        return self.combos[valid_indices[-1]] if valid_indices else None
    
    def sample_multiple(self, n: int, blocked_cards: Optional[List[Card]] = None, 
                       allow_overlaps: bool = False) -> List[Combo]:
        """
        Sample multiple combos
        抽样多个组合
        
        Args:
            n: Number of combos to sample
            blocked_cards: Initially blocked cards
            allow_overlaps: Whether to allow overlapping cards between samples
            
        Returns:
            List of sampled combos
        """
        results = []
        current_blocked = list(blocked_cards) if blocked_cards else []
        
        for _ in range(n):
            combo = self.sample(current_blocked)
            if combo is None:
                break
            
            results.append(combo)
            
            if not allow_overlaps:
                # Add this combo's cards to blocked list for next iteration
                current_blocked.extend(combo.cards)
        
        return results
    
    def get_statistics(self) -> Dict[str, float]:
        """Get statistics about the range"""
        if not self.combos:
            return {}
        
        total_weight = sum(combo.weight for combo in self.combos)
        
        return {
            'total_combos': len(self.combos),
            'total_weight': total_weight,
            'average_weight': total_weight / len(self.combos),
            'min_weight': min(combo.weight for combo in self.combos),
            'max_weight': max(combo.weight for combo in self.combos)
        }


def parse_ranges(range_expr: str) -> WeightedRangeSampler:
    """
    Convenience function to parse range and return sampler
    便利函数：解析范围并返回抽样器
    
    Args:
        range_expr: Range expression like "JJ+, ATs+, KQo, 54s-76s, A5s@30%"
        
    Returns:
        WeightedRangeSampler ready for sampling
    """
    parser = RangeParser()
    combos = parser.parse_range(range_expr)
    return WeightedRangeSampler(combos)