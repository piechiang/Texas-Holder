#!/usr/bin/env python3
"""
Poker Hand Range Parser for Texas Hold'em
德州扑克手牌范围解析器

This module provides functionality to parse and expand poker hand range strings
into specific hand combinations for equity calculations.

本模块提供解析和展开扑克手牌范围字符串为具体手牌组合的功能，用于权益计算。

Supported Range Syntax 支持的范围语法:
- Pocket pairs: AA, KK, QQ, 88+, 77-22, etc.
- Suited hands: AKs, KQs, T9s+, 54s-32s, etc. 
- Offsuit hands: AKo, KQo, T9o+, 54o-32o, etc.
- Any two cards: AK (includes both AKs and AKo)
- Multiple ranges: "AA-QQ, AKs, KQo+" (comma-separated)
- Percentage ranges: "15%", "25%", "50%" (top X% of hands)
- Named ranges: "UTG", "BTN", "SB", "BB" (position-based)
- Weighted ranges: "AA:0.5, KK:0.8" (with frequencies)
- Advanced syntax: "AK-A9, 22+, suited connectors"

Examples 示例:
- "AA" -> [(A♠,A♥), (A♠,A♦), (A♠,A♣), (A♥,A♦), (A♥,A♣), (A♦,A♣)]
- "QQ+" -> All pocket pairs from QQ to AA
- "AKs" -> All suited AK combinations
- "T9o-54o" -> All offsuit hands from T9 to 54
- "22+,AKs,KQo" -> All pocket pairs, suited AK, and offsuit KQ
- "15%" -> Top 15% of hands (AA-77, AK, AQ, etc.)
- "UTG" -> UTG opening range (~11% of hands)
- "suited connectors" -> 54s, 65s, 76s, etc.
- "AA:0.5" -> Pocket aces with 50% frequency
"""

import re
from enum import Enum
from itertools import combinations
from typing import List, Set, Tuple, Dict
from texas_holdem_calculator import Card, Rank, Suit

class RangeType(Enum):
    """Types of poker hand ranges"""
    POCKET_PAIR = "pair"
    SUITED = "suited" 
    OFFSUIT = "offsuit"
    ANY = "any"  # Both suited and offsuit
    PERCENTAGE = "percentage"  # Top X% of hands
    POSITION = "position"  # Position-based ranges
    WEIGHTED = "weighted"  # Hands with frequencies
    SPECIAL = "special"  # Special syntax like "suited connectors"

class WeightedHand:
    """Represents a hand with frequency weight"""
    def __init__(self, cards: Tuple[Card, Card], weight: float = 1.0):
        self.cards = cards
        self.weight = weight  # 0.0 to 1.0
    
    def __str__(self):
        return f"{self.cards[0]}{self.cards[1]} ({self.weight:.1%})"

class HandRange:
    """Enhanced poker hand range with advanced parsing and weighting capabilities"""
    
    def __init__(self, range_string: str = ""):
        """
        Initialize hand range from string with support for advanced syntax
        
        Args:
            range_string: Range notation like "AA-QQ, AKs, T9o+", "15%", "UTG", etc.
        """
        self.range_string = range_string.strip()
        self.combinations: List[Tuple[Card, Card]] = []
        self.weighted_combinations: List[WeightedHand] = []  # For frequency-based ranges
        self.is_weighted = False
        
        if self.range_string:
            self._parse_range_string(self.range_string)
    
    def _parse_range_string(self, range_str: str):
        """Parse enhanced range string with support for advanced syntax"""
        if not range_str:
            return
        
        # Check for special range types first
        if self._is_percentage_range(range_str):
            self._parse_percentage_range(range_str)
            return
        elif self._is_position_range(range_str):
            self._parse_position_range(range_str)
            return
        elif self._is_weighted_range(range_str):
            self._parse_weighted_range(range_str)
            return
        elif self._is_special_syntax(range_str):
            self._parse_special_syntax(range_str)
            return
            
        # Standard range parsing
        # Split by commas and clean up whitespace
        range_parts = [part.strip() for part in range_str.split(',') if part.strip()]
        
        all_combinations = []
        for part in range_parts:
            try:
                combinations = self._parse_single_range(part)
                all_combinations.extend(combinations)
            except ValueError as e:
                print(f"Warning: Could not parse range '{part}': {e}")
                continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_combinations = []
        for combo in all_combinations:
            # Normalize card order (lower rank first, same rank by suit)
            normalized = self._normalize_combination(combo)
            if normalized not in seen:
                seen.add(normalized)
                unique_combinations.append(combo)
        
        self.combinations = unique_combinations
    
    def _normalize_combination(self, combo: Tuple[Card, Card]) -> Tuple[tuple, tuple]:
        """Normalize card combination for deduplication"""
        c1, c2 = combo
        card1 = (c1.rank.value, c1.suit.value)
        card2 = (c2.rank.value, c2.suit.value)
        
        # Sort to ensure consistent ordering
        if card1 > card2:
            card1, card2 = card2, card1
            
        return (card1, card2)
    
    def _parse_single_range(self, range_part: str) -> List[Tuple[Card, Card]]:
        """Parse a single range part like 'AA', 'AKs+', 'T9o-54o'"""
        range_part = range_part.strip().upper()
        
        if not range_part:
            return []
        
        # Handle range modifiers (+ and -)
        if '+' in range_part:
            return self._parse_plus_range(range_part)
        elif '-' in range_part:
            return self._parse_dash_range(range_part)
        else:
            return self._parse_exact_hand(range_part)
    
    def _parse_plus_range(self, range_part: str) -> List[Tuple[Card, Card]]:
        """Parse plus ranges like 'QQ+', 'AKs+', 'T9o+'"""
        base_hand = range_part.replace('+', '').strip()
        
        if self._is_pocket_pair(base_hand):
            return self._expand_pocket_pair_plus(base_hand)
        else:
            return self._expand_broadway_plus(base_hand)
    
    def _parse_dash_range(self, range_part: str) -> List[Tuple[Card, Card]]:
        """Parse dash ranges like 'QQ-88', 'AKs-ATs', 'T9o-54o'"""
        if '-' not in range_part:
            return []
            
        parts = range_part.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid dash range format: {range_part}")
        
        start_hand, end_hand = [p.strip() for p in parts]
        
        if self._is_pocket_pair(start_hand) and self._is_pocket_pair(end_hand):
            return self._expand_pocket_pair_range(start_hand, end_hand)
        else:
            return self._expand_broadway_range(start_hand, end_hand)
    
    def _parse_exact_hand(self, hand: str) -> List[Tuple[Card, Card]]:
        """Parse exact hands like 'AA', 'AKs', 'AKo', 'AK'"""
        if self._is_pocket_pair(hand):
            return self._get_pocket_pair_combinations(hand)
        elif hand.upper().endswith('S'):
            return self._get_suited_combinations(hand[:-1])
        elif hand.upper().endswith('O'):
            return self._get_offsuit_combinations(hand[:-1])
        elif len(hand) == 2:
            # Any two cards (both suited and offsuit)
            suited = self._get_suited_combinations(hand)
            offsuit = self._get_offsuit_combinations(hand)
            return suited + offsuit
        else:
            raise ValueError(f"Invalid hand format: {hand}")
    
    def _is_pocket_pair(self, hand: str) -> bool:
        """Check if hand represents a pocket pair"""
        return len(hand) == 2 and hand[0] == hand[1]
    
    def _get_rank_value(self, rank_char: str) -> int:
        """Convert rank character to numeric value"""
        rank_map = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        return rank_map.get(rank_char.upper(), 0)
    
    def _get_rank_from_value(self, value: int) -> Rank:
        """Convert numeric value to Rank enum"""
        value_map = {
            2: Rank.TWO, 3: Rank.THREE, 4: Rank.FOUR, 5: Rank.FIVE,
            6: Rank.SIX, 7: Rank.SEVEN, 8: Rank.EIGHT, 9: Rank.NINE,
            10: Rank.TEN, 11: Rank.JACK, 12: Rank.QUEEN, 13: Rank.KING, 14: Rank.ACE
        }
        return value_map[value]
    
    def _get_pocket_pair_combinations(self, pair: str) -> List[Tuple[Card, Card]]:
        """Get all combinations for a pocket pair like 'AA'"""
        if len(pair) != 2 or pair[0] != pair[1]:
            return []
        
        rank_value = self._get_rank_value(pair[0])
        if rank_value == 0:
            return []
            
        rank = self._get_rank_from_value(rank_value)
        suits = list(Suit)
        
        # Generate all combinations of this rank with different suits
        combinations = []
        for i, suit1 in enumerate(suits):
            for suit2 in suits[i+1:]:
                combinations.append((Card(rank, suit1), Card(rank, suit2)))
        
        return combinations
    
    def _get_suited_combinations(self, cards: str) -> List[Tuple[Card, Card]]:
        """Get all suited combinations for hand like 'AK'"""
        if len(cards) != 2:
            return []
        
        rank1_val = self._get_rank_value(cards[0])
        rank2_val = self._get_rank_value(cards[1])
        
        if rank1_val == 0 or rank2_val == 0 or rank1_val == rank2_val:
            return []
        
        rank1 = self._get_rank_from_value(rank1_val)
        rank2 = self._get_rank_from_value(rank2_val)
        
        combinations = []
        for suit in Suit:
            combinations.append((Card(rank1, suit), Card(rank2, suit)))
        
        return combinations
    
    def _get_offsuit_combinations(self, cards: str) -> List[Tuple[Card, Card]]:
        """Get all offsuit combinations for hand like 'AK'"""
        if len(cards) != 2:
            return []
        
        rank1_val = self._get_rank_value(cards[0])
        rank2_val = self._get_rank_value(cards[1])
        
        if rank1_val == 0 or rank2_val == 0 or rank1_val == rank2_val:
            return []
        
        rank1 = self._get_rank_from_value(rank1_val)
        rank2 = self._get_rank_from_value(rank2_val)
        
        combinations = []
        for suit1 in Suit:
            for suit2 in Suit:
                if suit1 != suit2:
                    combinations.append((Card(rank1, suit1), Card(rank2, suit2)))
        
        return combinations
    
    def _expand_pocket_pair_plus(self, base_pair: str) -> List[Tuple[Card, Card]]:
        """Expand pocket pair plus ranges like 'QQ+'"""
        base_rank_val = self._get_rank_value(base_pair[0])
        if base_rank_val == 0:
            return []
        
        combinations = []
        for rank_val in range(base_rank_val, 15):  # Up to Ace (14)
            rank_char = self._get_rank_char(rank_val)
            pair = rank_char + rank_char
            combinations.extend(self._get_pocket_pair_combinations(pair))
        
        return combinations
    
    def _expand_pocket_pair_range(self, start_pair: str, end_pair: str) -> List[Tuple[Card, Card]]:
        """Expand pocket pair ranges like 'QQ-88'"""
        start_val = self._get_rank_value(start_pair[0])
        end_val = self._get_rank_value(end_pair[0])
        
        if start_val == 0 or end_val == 0:
            return []
        
        # Ensure start >= end (higher ranks first)
        if start_val < end_val:
            start_val, end_val = end_val, start_val
        
        combinations = []
        for rank_val in range(end_val, start_val + 1):
            rank_char = self._get_rank_char(rank_val)
            pair = rank_char + rank_char
            combinations.extend(self._get_pocket_pair_combinations(pair))
        
        return combinations
    
    def _expand_broadway_plus(self, base_hand: str) -> List[Tuple[Card, Card]]:
        """Expand suited/offsuit plus ranges like 'AKs+', 'T9o+'"""
        if len(base_hand) < 2:
            return []
        
        is_suited = base_hand.upper().endswith('S')
        is_offsuit = base_hand.upper().endswith('O')
        
        if is_suited or is_offsuit:
            cards = base_hand[:-1]
        else:
            cards = base_hand
            
        if len(cards) != 2:
            return []
        
        rank1_val = self._get_rank_value(cards[0])
        rank2_val = self._get_rank_value(cards[1])
        
        if rank1_val == 0 or rank2_val == 0:
            return []
        
        combinations = []
        
        # For connected hands, increment the kicker
        for kicker_val in range(rank2_val, rank1_val):
            kicker_char = self._get_rank_char(kicker_val)
            hand = cards[0] + kicker_char
            
            if is_suited:
                combinations.extend(self._get_suited_combinations(hand))
            elif is_offsuit:
                combinations.extend(self._get_offsuit_combinations(hand))
            else:
                # Include both suited and offsuit
                combinations.extend(self._get_suited_combinations(hand))
                combinations.extend(self._get_offsuit_combinations(hand))
        
        return combinations
    
    def _expand_broadway_range(self, start_hand: str, end_hand: str) -> List[Tuple[Card, Card]]:
        """Expand broadway ranges like 'AKs-ATs', 'T9o-54o'"""
        # Extract suited/offsuit modifier
        is_suited = start_hand.upper().endswith('S') and end_hand.upper().endswith('S')
        is_offsuit = start_hand.upper().endswith('O') and end_hand.upper().endswith('O')
        
        if is_suited:
            start_cards = start_hand[:-1]
            end_cards = end_hand[:-1]
        elif is_offsuit:
            start_cards = start_hand[:-1]
            end_cards = end_hand[:-1]
        else:
            start_cards = start_hand
            end_cards = end_hand
        
        if len(start_cards) != 2 or len(end_cards) != 2:
            return []
        
        # For simplicity, handle same high card ranges (like AK-AT)
        if start_cards[0] == end_cards[0]:
            high_card = start_cards[0]
            start_kicker_val = self._get_rank_value(start_cards[1])
            end_kicker_val = self._get_rank_value(end_cards[1])
            
            if start_kicker_val == 0 or end_kicker_val == 0:
                return []
            
            # Ensure start >= end (higher kickers first)
            if start_kicker_val < end_kicker_val:
                start_kicker_val, end_kicker_val = end_kicker_val, start_kicker_val
            
            combinations = []
            for kicker_val in range(end_kicker_val, start_kicker_val + 1):
                kicker_char = self._get_rank_char(kicker_val)
                hand = high_card + kicker_char
                
                if is_suited:
                    combinations.extend(self._get_suited_combinations(hand))
                elif is_offsuit:
                    combinations.extend(self._get_offsuit_combinations(hand))
                else:
                    combinations.extend(self._get_suited_combinations(hand))
                    combinations.extend(self._get_offsuit_combinations(hand))
            
            return combinations
        
        return []
    
    def _get_rank_char(self, rank_value: int) -> str:
        """Convert rank value back to character"""
        value_to_char = {
            2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
            10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'
        }
        return value_to_char.get(rank_value, '')
    
    def _is_percentage_range(self, range_str: str) -> bool:
        """Check if range is a percentage (e.g., '15%', '25%')"""
        return range_str.strip().endswith('%') and range_str.strip()[:-1].replace('.', '').isdigit()
    
    def _is_position_range(self, range_str: str) -> bool:
        """Check if range is a position-based range"""
        position_ranges = {'UTG', 'UTG+1', 'UTG+2', 'MP', 'MP+1', 'MP+2', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'}
        return range_str.strip().upper() in position_ranges
    
    def _is_weighted_range(self, range_str: str) -> bool:
        """Check if range contains frequency weights (e.g., 'AA:0.5, KK:0.8')"""
        return ':' in range_str and any(part.count(':') == 1 for part in range_str.split(','))
    
    def _is_special_syntax(self, range_str: str) -> bool:
        """Check if range uses special syntax"""
        special_keywords = {
            'suited connectors', 'suited connector', 'sc',
            'offsuit connectors', 'offsuit connector', 'oc',
            'suited aces', 'offsuit aces',
            'broadway', 'wheelies', 'low pairs'
        }
        return any(keyword in range_str.lower() for keyword in special_keywords)
    
    def _parse_percentage_range(self, range_str: str):
        """Parse percentage-based ranges (top X% of hands)"""
        try:
            percentage = float(range_str.strip()[:-1])
            if not 0 <= percentage <= 100:
                raise ValueError(f"Invalid percentage: {percentage}")
            
            # Get top X% of hands based on Sklansky-Malmuth rankings or modern preflop charts
            top_hands = self._get_top_percentage_hands(percentage)
            all_combinations = []
            
            for hand_str in top_hands:
                try:
                    combinations = self._parse_single_range(hand_str)
                    all_combinations.extend(combinations)
                except ValueError:
                    continue
            
            self.combinations = self._remove_duplicates(all_combinations)
            
        except ValueError as e:
            print(f"Error parsing percentage range '{range_str}': {e}")
    
    def _parse_position_range(self, range_str: str):
        """Parse position-based opening ranges"""
        position = range_str.strip().upper()
        
        # Modern 6-max opening ranges (simplified)
        position_ranges = {
            'UTG': "77+, ATs+, AJo+, KTs+, KQo, QTs+",
            'MP': "66+, A9s+, ATo+, K9s+, KJo+, Q9s+, QJo, J9s+, JTo, T9s",
            'CO': "55+, A2s+, A9o+, K7s+, KTo+, Q8s+, QTo+, J8s+, JTo, T8s+, T9o, 98s, 97s+",
            'BTN': "22+, A2s+, A2o+, K2s+, K8o+, Q2s+, Q9o+, J5s+, J9o+, T6s+, T9o, 95s+, 98o, 85s+, 87o, 75s+, 76o, 65s, 54s",
            'SB': "22+, A2s+, A2o+, K2s+, K5o+, Q2s+, Q8o+, J2s+, J8o+, T2s+, T8o+, 92s+, 97o+, 82s+, 86o+, 72s+, 76o, 62s+, 65o, 52s+, 54o, 42s+, 32s",
            'BB': "Any two cards"  # Depends on action, simplified
        }
        
        if position in position_ranges:
            if position == 'BB':
                # Generate all possible hands for BB (calling range depends on situation)
                self._generate_all_hands()
            else:
                self._parse_range_string(position_ranges[position])
        else:
            print(f"Unknown position: {position}")
    
    def _parse_weighted_range(self, range_str: str):
        """Parse ranges with frequency weights (e.g., 'AA:0.5, KK:0.8')"""
        self.is_weighted = True
        self.weighted_combinations = []
        
        parts = [part.strip() for part in range_str.split(',') if part.strip()]
        
        for part in parts:
            if ':' in part:
                hand_str, weight_str = part.split(':', 1)
                try:
                    weight = float(weight_str.strip())
                    if not 0 <= weight <= 1:
                        print(f"Warning: Weight {weight} not in range [0,1], clamping")
                        weight = max(0, min(1, weight))
                    
                    combinations = self._parse_single_range(hand_str.strip())
                    for combo in combinations:
                        self.weighted_combinations.append(WeightedHand(combo, weight))
                        
                except ValueError as e:
                    print(f"Error parsing weighted hand '{part}': {e}")
            else:
                # No weight specified, assume 1.0
                try:
                    combinations = self._parse_single_range(part)
                    for combo in combinations:
                        self.weighted_combinations.append(WeightedHand(combo, 1.0))
                except ValueError as e:
                    print(f"Error parsing hand '{part}': {e}")
        
        # Also populate regular combinations for compatibility
        self.combinations = [wh.cards for wh in self.weighted_combinations]
    
    def _parse_special_syntax(self, range_str: str):
        """Parse special range syntax like 'suited connectors'"""
        range_lower = range_str.lower().strip()
        combinations = []
        
        if 'suited connector' in range_lower or 'sc' == range_lower:
            # Suited connectors: 54s through JTs
            for rank1_val in range(5, 12):  # 5 through J
                rank2_val = rank1_val - 1
                rank1_char = self._get_rank_char(rank1_val)
                rank2_char = self._get_rank_char(rank2_val)
                hand_str = rank1_char + rank2_char + 's'
                try:
                    combinations.extend(self._parse_single_range(hand_str))
                except ValueError:
                    continue
        
        elif 'offsuit connector' in range_lower or 'oc' == range_lower:
            # Offsuit connectors
            for rank1_val in range(5, 12):
                rank2_val = rank1_val - 1
                rank1_char = self._get_rank_char(rank1_val)
                rank2_char = self._get_rank_char(rank2_val)
                hand_str = rank1_char + rank2_char + 'o'
                try:
                    combinations.extend(self._parse_single_range(hand_str))
                except ValueError:
                    continue
        
        elif 'suited aces' in range_lower:
            # All suited aces: A2s through AKs
            for rank_val in range(2, 14):
                rank_char = self._get_rank_char(rank_val)
                hand_str = 'A' + rank_char + 's'
                try:
                    combinations.extend(self._parse_single_range(hand_str))
                except ValueError:
                    continue
        
        elif 'offsuit aces' in range_lower:
            # All offsuit aces: A2o through AKo
            for rank_val in range(2, 14):
                rank_char = self._get_rank_char(rank_val)
                hand_str = 'A' + rank_char + 'o'
                try:
                    combinations.extend(self._parse_single_range(hand_str))
                except ValueError:
                    continue
        
        elif 'broadway' in range_lower:
            # Broadway cards: T, J, Q, K, A combinations
            broadway_ranks = ['T', 'J', 'Q', 'K', 'A']
            for i, rank1 in enumerate(broadway_ranks):
                for rank2 in broadway_ranks[i+1:]:
                    # Both suited and offsuit
                    for suffix in ['s', 'o']:
                        hand_str = rank1 + rank2 + suffix
                        try:
                            combinations.extend(self._parse_single_range(hand_str))
                        except ValueError:
                            continue
        
        elif 'low pairs' in range_lower:
            # Low pocket pairs: 22 through 66
            for rank_val in range(2, 7):
                rank_char = self._get_rank_char(rank_val)
                hand_str = rank_char + rank_char
                try:
                    combinations.extend(self._parse_single_range(hand_str))
                except ValueError:
                    continue
        
        self.combinations = self._remove_duplicates(combinations)
    
    def _get_top_percentage_hands(self, percentage: float) -> List[str]:
        """Get list of hands representing top X% based on modern preflop rankings"""
        # Simplified hand rankings - top hands in rough order
        all_hands_ranked = [
            # Premium pairs
            "AA", "KK", "QQ", "JJ", "TT",
            # Premium suited
            "AKs", "AQs", "AJs", "ATs", "KQs", "KJs", "KTs", "QJs", "QTs", "JTs",
            # Premium offsuit
            "AKo", "AQo", "AJo", "KQo",
            # Medium pairs
            "99", "88", "77", "66", "55", "44", "33", "22",
            # Medium suited
            "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
            "K9s", "Q9s", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s",
            # Medium offsuit
            "ATo", "KJo", "QJo", "JTo", "KTo", "QTo",
            # Remaining suited
            "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s",
            "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s",
            "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s",
            "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s",
            "97s", "96s", "95s", "94s", "93s", "92s",
            "86s", "85s", "84s", "83s", "82s",
            "75s", "74s", "73s", "72s",
            "64s", "63s", "62s",
            "53s", "52s",
            "43s", "42s",
            "32s",
            # Remaining offsuit (worst hands)
            "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o",
            "K9o", "Q9o", "J9o", "T9o", "98o", "87o", "76o", "65o", "54o",
            "K8o", "K7o", "K6o", "K5o", "K4o", "K3o", "K2o",
            "Q8o", "Q7o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o",
            "J8o", "J7o", "J6o", "J5o", "J4o", "J3o", "J2o",
            "T8o", "T7o", "T6o", "T5o", "T4o", "T3o", "T2o",
            "97o", "96o", "95o", "94o", "93o", "92o",
            "86o", "85o", "84o", "83o", "82o",
            "75o", "74o", "73o", "72o",
            "64o", "63o", "62o",
            "53o", "52o",
            "43o", "42o",
            "32o"
        ]
        
        # Calculate how many hands to include
        total_combinations = 1326  # Total possible starting hands in Hold'em
        target_combinations = int((percentage / 100) * total_combinations)
        
        # Count combinations for each hand type and include until we reach target
        included_hands = []
        current_combinations = 0
        
        for hand in all_hands_ranked:
            hand_combinations = self._count_hand_combinations(hand)
            if current_combinations + hand_combinations <= target_combinations:
                included_hands.append(hand)
                current_combinations += hand_combinations
            else:
                break
        
        return included_hands
    
    def _count_hand_combinations(self, hand_str: str) -> int:
        """Count number of combinations for a hand string"""
        if len(hand_str) == 2 and hand_str[0] == hand_str[1]:  # Pocket pair
            return 6
        elif hand_str.endswith('s'):  # Suited
            return 4
        elif hand_str.endswith('o'):  # Offsuit
            return 12
        else:  # Any (both suited and offsuit)
            return 16
    
    def _generate_all_hands(self):
        """Generate all possible starting hands (for BB calling range)"""
        all_combinations = []
        
        # Generate all pocket pairs
        for rank in Rank:
            for suit1, suit2 in combinations(Suit, 2):
                all_combinations.append((Card(rank, suit1), Card(rank, suit2)))
        
        # Generate all non-pair combinations
        for rank1, rank2 in combinations(Rank, 2):
            for suit1 in Suit:
                for suit2 in Suit:
                    all_combinations.append((Card(rank1, suit1), Card(rank2, suit2)))
        
        self.combinations = all_combinations
    
    def _remove_duplicates(self, combinations: List[Tuple[Card, Card]]) -> List[Tuple[Card, Card]]:
        """Remove duplicate combinations while preserving order"""
        seen = set()
        unique_combinations = []
        for combo in combinations:
            normalized = self._normalize_combination(combo)
            if normalized not in seen:
                seen.add(normalized)
                unique_combinations.append(combo)
        return unique_combinations
    
    def get_combinations(self) -> List[Tuple[Card, Card]]:
        """Get all card combinations in this range"""
        return self.combinations
    
    def get_weighted_combinations(self) -> List[WeightedHand]:
        """Get weighted combinations if this is a weighted range"""
        return self.weighted_combinations if self.is_weighted else []
    
    def size(self) -> int:
        """Get number of combinations in this range"""
        return len(self.combinations)
    
    def intersects_with(self, other_cards: List[Card]) -> bool:
        """Check if any combination in this range conflicts with given cards"""
        used_cards = set(other_cards)
        
        for c1, c2 in self.combinations:
            if c1 in used_cards or c2 in used_cards:
                return True
        return False
    
    def remove_conflicting(self, other_cards: List[Card]) -> 'HandRange':
        """Create new range with combinations that don't conflict with given cards"""
        used_cards = set(other_cards)
        valid_combinations = []
        
        for c1, c2 in self.combinations:
            if c1 not in used_cards and c2 not in used_cards:
                valid_combinations.append((c1, c2))
        
        new_range = HandRange()
        new_range.range_string = f"{self.range_string} (filtered)"
        new_range.combinations = valid_combinations
        return new_range
    
    def get_effective_size(self) -> float:
        """Get effective size considering weights"""
        if self.is_weighted:
            return sum(wh.weight for wh in self.weighted_combinations)
        return len(self.combinations)
    
    def get_frequency(self, cards: Tuple[Card, Card]) -> float:
        """Get frequency/weight for specific hand combination"""
        if self.is_weighted:
            for wh in self.weighted_combinations:
                if wh.cards == cards:
                    return wh.weight
            return 0.0
        return 1.0 if cards in self.combinations else 0.0
    
    def __str__(self) -> str:
        """Enhanced string representation of the range"""
        if self.is_weighted:
            return f"WeightedRange('{self.range_string}') - {len(self.weighted_combinations)} hands, {self.get_effective_size():.1f} effective"
        return f"Range('{self.range_string}') - {self.size()} combinations"
    
    def __repr__(self) -> str:
        return self.__str__()

def parse_ranges(range_string: str) -> HandRange:
    """
    Convenience function to parse range string
    
    Args:
        range_string: Range notation like "AA-QQ, AKs, T9o+"
        
    Returns:
        HandRange object with parsed combinations
        
    Examples:
        >>> range = parse_ranges("AA, AKs")
        >>> print(f"Range has {range.size()} combinations")
        >>> combos = range.get_combinations()
    """
    return HandRange(range_string)

def calculate_range_vs_range_equity(hero_range: str, villain_range: str, 
                                  community_cards: List[Card] = None,
                                  num_simulations: int = 10000,
                                  consider_weights: bool = True) -> Dict:
    """
    Calculate equity between two hand ranges
    
    Args:
        hero_range: Hero's range string (e.g. "AA-QQ, AKs")
        villain_range: Villain's range string (e.g. "22+, A2s+")
        community_cards: Board cards (if any)
        num_simulations: Number of Monte Carlo simulations
        
    Returns:
        Dictionary with equity results
    """
    from texas_holdem_calculator import TexasHoldemCalculator
    
    if community_cards is None:
        community_cards = []
    
    hero_hands = parse_ranges(hero_range)
    villain_hands = parse_ranges(villain_range)
    
    # Remove conflicting combinations with community cards
    hero_hands = hero_hands.remove_conflicting(community_cards)
    villain_hands = villain_hands.remove_conflicting(community_cards)
    
    if hero_hands.size() == 0 or villain_hands.size() == 0:
        return {
            "error": "No valid combinations remain after filtering board cards",
            "hero_combos": hero_hands.size(),
            "villain_combos": villain_hands.size()
        }
    
    calculator = TexasHoldemCalculator()
    total_hero_equity = 0.0
    total_combinations = 0
    
    hero_combos = hero_hands.get_combinations()
    villain_combos = villain_hands.get_combinations()
    
    for hero_combo in hero_combos:
        for villain_combo in villain_combos:
            # Check for card conflicts
            all_cards = list(hero_combo) + list(villain_combo) + community_cards
            if len(set(all_cards)) != len(all_cards):
                continue  # Skip conflicting combinations
            
            # Calculate equity for this specific matchup
            result = calculator.calculate_win_probability(
                hole_cards=list(hero_combo),
                community_cards=community_cards,
                num_opponents=1,
                num_simulations=num_simulations // max(1, len(hero_combos) * len(villain_combos) // 100)
            )
            
            hero_equity = result['win_probability'] + 0.5 * result['tie_probability']
            total_hero_equity += hero_equity
            total_combinations += 1
    
    if total_combinations == 0:
        return {
            "error": "No valid combination matchups found",
            "hero_combos": hero_hands.size(),
            "villain_combos": villain_hands.size()
        }
    
    avg_hero_equity = total_hero_equity / total_combinations
    avg_villain_equity = 1.0 - avg_hero_equity
    
    return {
        "hero_range": hero_range,
        "villain_range": villain_range,
        "hero_equity": avg_hero_equity,
        "villain_equity": avg_villain_equity,
        "hero_combos": hero_hands.size(),
        "villain_combos": villain_hands.size(),
        "total_matchups": total_combinations,
        "simulations_per_matchup": num_simulations // max(1, len(hero_combos) * len(villain_combos) // 100)
    }

if __name__ == "__main__":
    # Example usage and testing
    print("🎯 Range Parser Example Usage")
    print("=" * 50)
    
    test_ranges = [
        "AA",
        "QQ+", 
        "77-22",
        "AKs",
        "AKo",
        "AK",
        "AKs-ATs",
        "T9o+",
        "AA-QQ, AKs, KQo+"
    ]
    
    for range_str in test_ranges:
        try:
            range_obj = parse_ranges(range_str)
            print(f"Range '{range_str}': {range_obj.size()} combinations")
            
            # Show first few combinations as examples
            combos = range_obj.get_combinations()[:3]
            combo_strs = [f"{c1}{c2}" for c1, c2 in combos]
            if range_obj.size() > 3:
                combo_strs.append("...")
            print(f"  Examples: {', '.join(combo_strs)}")
            print()
            
        except Exception as e:
            print(f"Error parsing '{range_str}': {e}")
            print()
    
    # Example range vs range calculation
    print("\n🥊 Range vs Range Equity Example")
    print("-" * 50)
    
    try:
        result = calculate_range_vs_range_equity(
            hero_range="AA-QQ",
            villain_range="22+,AKs,AKo", 
            num_simulations=1000  # Reduced for demo
        )
        
        if "error" not in result:
            print(f"Hero Range: {result['hero_range']} ({result['hero_combos']} combos)")
            print(f"Villain Range: {result['villain_range']} ({result['villain_combos']} combos)")
            print(f"Hero Equity: {result['hero_equity']:.1%}")
            print(f"Villain Equity: {result['villain_equity']:.1%}")
            print(f"Total Matchups: {result['total_matchups']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Error in range vs range calculation: {e}")
    
    # Test enhanced ranges
    print("\n🚀 Enhanced Range Syntax Examples:")
    enhanced_examples = ["15%", "UTG", "suited connectors", "AA:0.5, KK", "broadway"]
    
    for range_str in enhanced_examples:
        try:
            range_obj = parse_ranges(range_str)
            if range_obj.is_weighted:
                print(f"Weighted '{range_str}': {range_obj.get_effective_size():.1f} effective combos")
            else:
                print(f"Enhanced '{range_str}': {range_obj.size()} combinations")
        except Exception as e:
            print(f"Note: {range_str} not fully implemented yet: {e}")