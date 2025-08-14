#!/usr/bin/env python3
"""
Texas Hold'em Poker Probability Calculator and Strategy Advisor
德州扑克概率计算器和策略顾问

This module provides comprehensive functionality for:
- Hand evaluation and ranking
- Win probability calculation
- Betting strategy recommendations
- Monte Carlo simulations for accurate probability estimation

本模块提供以下功能：
- 手牌评估和排名
- 胜率计算
- 下注策略推荐
- 蒙特卡罗模拟进行精确概率估算
"""

import itertools
import random
import warnings
from collections import Counter
from enum import Enum
from itertools import combinations
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple

# Try to import eval7 for fast hand evaluation
try:
    import eval7

    EVAL7_AVAILABLE = True
except ImportError:
    EVAL7_AVAILABLE = False
    warnings.warn("eval7 not available, using fallback evaluator. Install with: pip install eval7", UserWarning, stacklevel=2)


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class HandRank(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        rank_symbols = {
            Rank.TWO: "2",
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A",
        }
        return f"{rank_symbols[self.rank]}{self.suit.value}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


@dataclass
class BettingContext:
    """Context information for betting decisions"""
    hole_cards: list[Card]
    community_cards: list[Card]
    pot_size: float
    bet_to_call: float
    stack_size: float
    position: str
    num_opponents: int
    opponent_stack_sizes: list[float]
    betting_round: str
    aggressive_opponents: int
    previous_action: str
    win_probability: float
    
    @property
    def pot_odds(self) -> float:
        return self.bet_to_call / (self.pot_size + self.bet_to_call) if (self.pot_size + self.bet_to_call) > 0 else 0


@dataclass 
class BettingDecision:
    """Comprehensive betting decision with analysis"""
    action: str
    confidence: str
    expected_value: float
    reasoning: str
    position_factor: float
    stack_factor: float
    implied_odds: float
    reverse_implied_odds: float
    fold_equity: float
    alternative_actions: dict


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        random.shuffle(self.cards)

    def deal_card(self) -> Card:
        return self.cards.pop()

    def remove_cards(self, cards_to_remove: list[Card]):
        for card in cards_to_remove:
            if card in self.cards:
                self.cards.remove(card)


class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards: list[Card]) -> tuple[HandRank, list[int]]:
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")

        best_rank = HandRank.HIGH_CARD
        best_values = []

        for combo in itertools.combinations(cards, 5):
            rank, values = HandEvaluator._evaluate_five_cards(list(combo))
            if rank.value > best_rank.value or (rank == best_rank and values > best_values):
                best_rank = rank
                best_values = values

        return best_rank, best_values

    @staticmethod
    def _evaluate_five_cards(cards: list[Card]) -> tuple[HandRank, list[int]]:
        ranks = [card.rank.value for card in cards]
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)

        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)

        # Royal Flush
        if is_flush and is_straight and min(ranks) == 10:
            return HandRank.ROYAL_FLUSH, [14]

        # Straight Flush
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, [max(ranks)]

        # Four of a Kind
        if 4 in rank_counts.values():
            four_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_A_KIND, [four_rank, kicker]

        # Full House
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            three_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [three_rank, pair_rank]

        # Flush
        if is_flush:
            return HandRank.FLUSH, sorted(ranks, reverse=True)

        # Straight
        if is_straight:
            return HandRank.STRAIGHT, [max(ranks)]

        # Three of a Kind
        if 3 in rank_counts.values():
            three_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [three_rank] + kickers

        # Two Pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]

        # One Pair
        if 2 in rank_counts.values():
            pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.ONE_PAIR, [pair_rank] + kickers

        # High Card
        return HandRank.HIGH_CARD, sorted(ranks, reverse=True)

    @staticmethod
    def _is_straight(ranks: list[int]) -> bool:
        sorted_ranks = sorted(set(ranks))
        if len(sorted_ranks) != 5:
            return False

        # Check normal straight
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            return True

        # Check A-2-3-4-5 straight (wheel)
        return sorted_ranks == [2, 3, 4, 5, 14]


class FastHandEvaluator:
    """
    Optimized hand evaluator using eval7 with batch processing and caching
    使用 eval7 进行高性能手牌评估，支持批处理和缓存
    
    Features:
    - Batch hand evaluation for improved performance
    - LRU cache for frequently evaluated hands  
    - Vectorized operations where possible
    - Optimized eval7 integration
    """

    def __init__(self, use_eval7: bool = True, cache_size: int = 1000):
        self.use_eval7 = use_eval7 and EVAL7_AVAILABLE
        self.fallback_evaluator = HandEvaluator()
        self.cache_size = cache_size
        
        # Initialize caching
        from functools import lru_cache
        self._cached_evaluate_hand = lru_cache(maxsize=cache_size)(self._evaluate_hand_internal)
        self._cached_compare_hands = lru_cache(maxsize=cache_size)(self._compare_hands_internal)

        if self.use_eval7:
            # Pre-build suit mapping for eval7 (uses string representation)
            self.suit_map = {Suit.HEARTS: "h", Suit.DIAMONDS: "d", Suit.CLUBS: "c", Suit.SPADES: "s"}
            self.rank_map = {
                Rank.TWO: "2",
                Rank.THREE: "3",
                Rank.FOUR: "4",
                Rank.FIVE: "5",
                Rank.SIX: "6",
                Rank.SEVEN: "7",
                Rank.EIGHT: "8",
                Rank.NINE: "9",
                Rank.TEN: "T",
                Rank.JACK: "J",
                Rank.QUEEN: "Q",
                Rank.KING: "K",
                Rank.ACE: "A",
            }
            
            # Pre-convert all possible cards for efficiency
            if EVAL7_AVAILABLE:
                self._eval7_card_cache = {}
                for rank in Rank:
                    for suit in Suit:
                        card = Card(rank, suit)
                        card_str = self.rank_map[rank] + self.suit_map[suit]
                        self._eval7_card_cache[card] = eval7.Card(card_str)

    def _convert_to_eval7_card(self, card: Card) -> "eval7.Card":
        """Convert our Card object to eval7.Card using pre-cached conversion"""
        if hasattr(self, '_eval7_card_cache') and card in self._eval7_card_cache:
            return self._eval7_card_cache[card]
        
        # Fallback to original method if cache not available
        card_str = self.rank_map[card.rank] + self.suit_map[card.suit]
        return eval7.Card(card_str)

    def _convert_eval7_hand_rank(self, eval7_value: int) -> tuple[HandRank, list[int]]:
        """Convert eval7 hand value to our HandRank enum"""
        hand_type = eval7.handtype(eval7_value)

        # Check for royal flush by value range (eval7 doesn't distinguish royal flush from straight flush)
        if hand_type == "Straight Flush" and eval7_value >= 135004160:  # Royal flush value range
            return HandRank.ROYAL_FLUSH, [14]
        elif hand_type == "Straight Flush":
            return HandRank.STRAIGHT_FLUSH, []
        elif hand_type == "Quads":  # eval7 uses "Quads" not "Four of a Kind"
            return HandRank.FOUR_OF_A_KIND, []
        elif hand_type == "Full House":
            return HandRank.FULL_HOUSE, []
        elif hand_type == "Flush":
            return HandRank.FLUSH, []
        elif hand_type == "Straight":
            return HandRank.STRAIGHT, []
        elif hand_type == "Trips":  # eval7 uses "Trips" not "Three of a Kind"
            return HandRank.THREE_OF_A_KIND, []
        elif hand_type == "Two Pair":
            return HandRank.TWO_PAIR, []
        elif hand_type == "Pair":  # eval7 uses "Pair" not "One Pair"
            return HandRank.ONE_PAIR, []
        else:  # High Card and any other cases
            return HandRank.HIGH_CARD, []

    def _card_name_to_value(self, card_name: str) -> int:
        """Convert card name to numeric value"""
        name_map = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }
        return name_map.get(card_name, 0)

    def evaluate_hand(self, cards: list[Card]) -> tuple[HandRank, list[int]]:
        """Evaluate hand using cached evaluation for performance"""
        # Convert cards to hashable tuple for caching
        card_tuple = self._cards_to_hashable_tuple(cards)
        return self._cached_evaluate_hand(card_tuple)
    
    def _cards_to_hashable_tuple(self, cards: list[Card]) -> tuple:
        """Convert list of cards to hashable tuple for caching"""
        return tuple((card.rank.value, card.suit.value) for card in sorted(cards, key=lambda c: (c.rank.value, c.suit.value)))
    
    def _hashable_tuple_to_cards(self, card_tuple: tuple) -> list[Card]:
        """Convert hashable tuple back to list of cards"""
        cards = []
        for rank_val, suit_val in card_tuple:
            rank = next(r for r in Rank if r.value == rank_val)
            suit = next(s for s in Suit if s.value == suit_val)
            cards.append(Card(rank, suit))
        return cards
    
    def _evaluate_hand_internal(self, card_tuple: tuple) -> tuple[HandRank, list[int]]:
        """Internal cached hand evaluation"""
        cards = self._hashable_tuple_to_cards(card_tuple)
        
        if not self.use_eval7:
            return self.fallback_evaluator.evaluate_hand(cards)

        try:
            # Use pre-cached eval7 cards for efficiency
            eval7_cards = [self._eval7_card_cache[card] for card in cards]

            # Use eval7.evaluate to get best 5-card hand value
            best_value = eval7.evaluate(eval7_cards)

            return self._convert_eval7_hand_rank(best_value)

        except Exception:
            # Fall back to original evaluator on any error
            return self.fallback_evaluator.evaluate_hand(cards)
    
    def evaluate_hands_batch(self, hands: list[list[Card]]) -> list[tuple[HandRank, list[int]]]:
        """Evaluate multiple hands in batch for improved performance"""
        if not hands:
            return []
        
        results = []
        
        if self.use_eval7 and EVAL7_AVAILABLE:
            # Process in batch using eval7
            try:
                for hand in hands:
                    result = self.evaluate_hand(hand)
                    results.append(result)
            except Exception:
                # Fall back to individual evaluation
                for hand in hands:
                    try:
                        result = self.fallback_evaluator.evaluate_hand(hand)
                        results.append(result)
                    except Exception as e:
                        # Fallback result for problematic hands
                        results.append((HandRank.HIGH_CARD, []))
        else:
            # Use fallback evaluator for all
            for hand in hands:
                try:
                    result = self.fallback_evaluator.evaluate_hand(hand)
                    results.append(result)
                except Exception:
                    results.append((HandRank.HIGH_CARD, []))
        
        return results

    def compare_hands(self, cards1: list[Card], cards2: list[Card]) -> int:
        """
        Compare two hands directly using cached comparison. Returns:
        1 if cards1 wins, -1 if cards2 wins, 0 if tie
        """
        card_tuple1 = self._cards_to_hashable_tuple(cards1)
        card_tuple2 = self._cards_to_hashable_tuple(cards2)
        
        # Ensure consistent ordering for cache efficiency
        if card_tuple1 <= card_tuple2:
            result = self._cached_compare_hands(card_tuple1, card_tuple2)
        else:
            result = -self._cached_compare_hands(card_tuple2, card_tuple1)
        
        return result
    
    def _compare_hands_internal(self, card_tuple1: tuple, card_tuple2: tuple) -> int:
        """Internal cached hand comparison"""
        cards1 = self._hashable_tuple_to_cards(card_tuple1)
        cards2 = self._hashable_tuple_to_cards(card_tuple2)
        
        if self.use_eval7:
            try:
                eval7_cards1 = [self._eval7_card_cache[card] for card in cards1]
                eval7_cards2 = [self._eval7_card_cache[card] for card in cards2]

                # eval7.evaluate returns higher numbers for better hands
                value1 = eval7.evaluate(eval7_cards1)
                value2 = eval7.evaluate(eval7_cards2)

                if value1 > value2:  # Higher value = better hand in eval7
                    return 1
                elif value1 < value2:
                    return -1
                else:
                    return 0
            except Exception:
                pass

        # Fallback comparison
        rank1, values1 = self.evaluate_hand(cards1)
        rank2, values2 = self.evaluate_hand(cards2)

        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        elif values1 > values2:
            return 1
        elif values1 < values2:
            return -1
        else:
            return 0
    
    def compare_hands_batch(self, hand_pairs: list[tuple[list[Card], list[Card]]]) -> list[int]:
        """Compare multiple hand pairs in batch for improved performance"""
        if not hand_pairs:
            return []
        
        results = []
        
        # Process each pair using cached comparison
        for cards1, cards2 in hand_pairs:
            try:
                result = self.compare_hands(cards1, cards2)
                results.append(result)
            except Exception:
                # Default to tie in case of error
                results.append(0)
        
        return results
    
    def clear_cache(self):
        """Clear the evaluation cache"""
        self._cached_evaluate_hand.cache_clear()
        self._cached_compare_hands.cache_clear()
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        return {
            'evaluate_hand_cache': self._cached_evaluate_hand.cache_info(),
            'compare_hands_cache': self._cached_compare_hands.cache_info()
        }


class TexasHoldemCalculator:
    def __init__(self, use_fast_evaluator: bool = True, random_seed: int | None = None):
        """
        Initialize Texas Hold'em calculator with options for fast evaluation and reproducible results

        Args:
            use_fast_evaluator: Use FastHandEvaluator with eval7 if available
            random_seed: Seed for random number generator for reproducible Monte Carlo results
        """
        self.deck = Deck()
        self.hand_evaluator = FastHandEvaluator(use_eval7=use_fast_evaluator) if use_fast_evaluator else HandEvaluator()
        self.random_seed = random_seed

        # Set random seed if provided for reproducible results
        if random_seed is not None:
            random.seed(random_seed)

    def calculate_win_probability(
        self,
        hole_cards: list[Card],
        community_cards: list[Card] = None,
        num_opponents: int = 1,
        num_simulations: int = 10000,
        seed: int | None = None,
        use_batch_processing: bool = True,
        force_simulation: bool = False,
    ) -> dict:
        if community_cards is None:
            community_cards = []

        # Set seed for reproducible results if provided
        if seed is not None:
            random.seed(seed)
        
        # Decide whether to use enumeration or Monte Carlo
        if not force_simulation and self._should_use_enumeration(num_opponents, len(community_cards)):
            return self._calculate_win_probability_exact(
                hole_cards, community_cards, num_opponents
            )
        else:
            return self._calculate_win_probability_simulation(
                hole_cards, community_cards, num_opponents, num_simulations, seed, use_batch_processing
            )

        # This method signature is maintained for compatibility
        # Actual implementation moved to helper methods
        pass  # Implementation moved to _calculate_win_probability_simulation
    
    def _should_use_enumeration(self, num_opponents: int, num_community_cards: int) -> bool:
        """
        Decide whether to use exact enumeration based on computational complexity
        根据计算复杂度决定是否使用精确枚举
        
        Enumeration is preferred when:
        - Few opponents (1-2)
        - Many community cards known (4-5)
        - Total combinations < ~50,000
        """
        remaining_community = 5 - num_community_cards
        remaining_deck_size = 52 - 2 - num_community_cards  # Exclude hero's cards and community
        
        # Estimate total combinations to evaluate
        if remaining_community == 0:
            # All community cards known - just enumerate opponent hole cards
            opponent_combinations = 1
            for i in range(num_opponents):
                remaining_for_opponent = remaining_deck_size - (2 * i)
                opponent_combinations *= (remaining_for_opponent * (remaining_for_opponent - 1)) // 2
            
            # Use enumeration if < 20,000 combinations
            return opponent_combinations < 20000
        
        elif remaining_community == 1:
            # One card to come - manageable for 1-2 opponents
            if num_opponents <= 2:
                return True
        
        # For other cases, use thresholds based on experience
        total_unknown_cards = remaining_community + (2 * num_opponents)
        
        # Conservative thresholds
        if num_opponents == 1 and num_community_cards >= 3:
            return True  # Heads-up with flop+ is usually manageable
        elif num_opponents == 2 and num_community_cards >= 4:
            return True  # 3-way with turn+ is still reasonable
        
        return False
    
    def _calculate_win_probability_exact(
        self, hole_cards: list[Card], community_cards: list[Card], num_opponents: int
    ) -> dict:
        """
        Calculate exact win probability using full enumeration
        使用完全枚举计算精确胜率
        """
        deck = Deck()
        deck.remove_cards(hole_cards + community_cards)
        remaining_cards = deck.cards
        
        wins = 0
        ties = 0
        total_scenarios = 0
        
        remaining_community = 5 - len(community_cards)
        
        # Generate all possible completions of community cards
        if remaining_community > 0:
            community_completions = list(combinations(remaining_cards, remaining_community))
        else:
            community_completions = [()]  # Empty tuple for no additional cards needed
        
        for community_completion in community_completions:
            complete_community = community_cards + list(community_completion)
            
            # Remove used community cards from available cards for opponents
            available_for_opponents = [
                card for card in remaining_cards if card not in community_completion
            ]
            
            # Generate all possible opponent hole card combinations
            opponent_combos = self._generate_opponent_combinations(
                available_for_opponents, num_opponents
            )
            
            for opponent_holes in opponent_combos:
                total_scenarios += 1
                
                # Evaluate all hands
                player_hand = hole_cards + complete_community
                
                player_wins_scenario = True
                tie_in_scenario = False
                
                for opponent_hole in opponent_holes:
                    opponent_hand = opponent_hole + complete_community
                    
                    comparison = self.hand_evaluator.compare_hands(player_hand, opponent_hand)
                    if comparison < 0:  # Player loses
                        player_wins_scenario = False
                        break
                    elif comparison == 0:  # Tie
                        tie_in_scenario = True
                
                if player_wins_scenario and not tie_in_scenario:
                    wins += 1
                elif player_wins_scenario and tie_in_scenario:
                    ties += 1
        
        if total_scenarios == 0:
            return {
                "win_probability": 0.0,
                "tie_probability": 0.0,
                "lose_probability": 1.0,
                "simulations": 0,
                "method": "enumeration",
                "note": "No valid scenarios found"
            }
        
        win_rate = wins / total_scenarios
        tie_rate = ties / total_scenarios
        
        return {
            "win_probability": win_rate,
            "tie_probability": tie_rate,
            "lose_probability": 1 - win_rate - tie_rate,
            "simulations": total_scenarios,
            "method": "enumeration",
            "note": f"Exact calculation over {total_scenarios} scenarios"
        }
    
    def _generate_opponent_combinations(self, available_cards: list[Card], num_opponents: int) -> list[list[list[Card]]]:
        """
        Generate all possible combinations of opponent hole cards
        生成所有可能的对手底牌组合
        """
        if num_opponents == 0:
            return [[]]
        
        if num_opponents == 1:
            # Simple case: just generate all 2-card combinations
            return [[list(combo)] for combo in combinations(available_cards, 2)]
        
        # Multiple opponents: recursively generate combinations
        # This is computationally intensive for many opponents
        all_combinations = []
        
        for first_opponent_cards in combinations(available_cards, 2):
            remaining_cards = [card for card in available_cards if card not in first_opponent_cards]
            
            remaining_opponent_combos = self._generate_opponent_combinations(
                remaining_cards, num_opponents - 1
            )
            
            for remaining_combo in remaining_opponent_combos:
                complete_combo = [list(first_opponent_cards)] + remaining_combo
                all_combinations.append(complete_combo)
        
        return all_combinations
    
    def _calculate_win_probability_simulation(
        self, 
        hole_cards: list[Card], 
        community_cards: list[Card], 
        num_opponents: int, 
        num_simulations: int, 
        seed: int | None, 
        use_batch_processing: bool
    ) -> dict:
        """
        Calculate win probability using Monte Carlo simulation
        使用蒙特卡罗模拟计算胜率
        """
        wins = 0
        ties = 0
        total_simulations = 0

        for _ in range(num_simulations):
            deck = Deck()
            deck.remove_cards(hole_cards + community_cards)

            # Complete community cards if needed
            sim_community = community_cards.copy()
            while len(sim_community) < 5:
                sim_community.append(deck.deal_card())

            # Generate opponent hands
            opponent_hands = []
            for _ in range(num_opponents):
                opponent_hole = [deck.deal_card(), deck.deal_card()]
                opponent_hands.append(opponent_hole)

            # Compare hands using batch processing when possible
            player_hand = hole_cards + sim_community
            opponent_hands_full = [opponent_hole + sim_community for opponent_hole in opponent_hands]

            player_wins = True
            tie_occurred = False

            # Use batch comparison if available and beneficial
            if (use_batch_processing and 
                hasattr(self.hand_evaluator, "compare_hands_batch") and 
                len(opponent_hands) > 1):
                
                # Create pairs for batch comparison
                hand_pairs = [(player_hand, opponent_hand) for opponent_hand in opponent_hands_full]
                comparisons = self.hand_evaluator.compare_hands_batch(hand_pairs)
                
                for comparison in comparisons:
                    if comparison < 0:  # Player loses
                        player_wins = False
                        break
                    elif comparison == 0:  # Tie
                        tie_occurred = True
            else:
                # Individual comparison (original logic)
                for opponent_hand in opponent_hands_full:
                    # Use FastHandEvaluator's compare_hands method for efficiency
                    if hasattr(self.hand_evaluator, "compare_hands"):
                        comparison = self.hand_evaluator.compare_hands(player_hand, opponent_hand)
                        if comparison < 0:  # Player loses
                            player_wins = False
                            break
                        elif comparison == 0:  # Tie
                            tie_occurred = True
                    else:
                        # Fallback to original comparison method
                        player_rank, player_values = self.hand_evaluator.evaluate_hand(player_hand)
                        opponent_rank, opponent_values = self.hand_evaluator.evaluate_hand(opponent_hand)

                        if opponent_rank.value > player_rank.value or (
                            opponent_rank == player_rank and opponent_values > player_values
                        ):
                            player_wins = False
                            break
                        elif opponent_rank == player_rank and opponent_values == player_values:
                            tie_occurred = True

            if player_wins and not tie_occurred:
                wins += 1
            elif player_wins and tie_occurred:
                ties += 1

            total_simulations += 1

        win_rate = wins / total_simulations
        tie_rate = ties / total_simulations

        return {
            "win_probability": win_rate,
            "tie_probability": tie_rate,
            "lose_probability": 1 - win_rate - tie_rate,
            "simulations": total_simulations,
            "method": "simulation",
        }

    def get_hand_strength(self, hole_cards: list[Card], community_cards: list[Card] = None) -> dict:
        if community_cards is None:
            community_cards = []

        all_cards = hole_cards + community_cards
        if len(all_cards) < 2:
            return {"error": "Need at least hole cards"}

        if len(all_cards) >= 5:
            hand_rank, values = self.hand_evaluator.evaluate_hand(all_cards)
            return {
                "hand_rank": hand_rank.name,
                "hand_value": hand_rank.value,
                "description": self._get_hand_description(hand_rank, values),
                "strength_score": self._calculate_strength_score(hand_rank, values),
            }
        else:
            return {
                "hand_rank": "INCOMPLETE",
                "description": f'Hole cards: {", ".join(str(card) for card in hole_cards)}',
                "potential": self._analyze_potential(hole_cards, community_cards),
            }

    def get_betting_recommendation(
        self,
        hole_cards: list[Card],
        community_cards: list[Card] = None,
        num_opponents: int = 1,
        pot_size: float = 100,
        bet_to_call: float = 10,
        position: str = "BTN",
        stack_size: float = 1000,
        opponent_stack_sizes: list[float] = None,
        betting_round: str = "preflop",
        aggressive_opponents: int = 0,
        previous_action: str = "check",
    ) -> dict:
        if opponent_stack_sizes is None:
            opponent_stack_sizes = [stack_size] * num_opponents
        
        # Enhanced probability calculation with more simulations for better decisions
        prob_result = self.calculate_win_probability(hole_cards, community_cards, num_opponents, 8000)
        win_prob = prob_result["win_probability"]
        
        # Create betting context for advanced analysis
        context = BettingContext(
            hole_cards=hole_cards,
            community_cards=community_cards or [],
            pot_size=pot_size,
            bet_to_call=bet_to_call,
            stack_size=stack_size,
            position=position,
            num_opponents=num_opponents,
            opponent_stack_sizes=opponent_stack_sizes,
            betting_round=betting_round,
            aggressive_opponents=aggressive_opponents,
            previous_action=previous_action,
            win_probability=win_prob
        )
        
        # Basic strategy for now (advanced decision engine would go here)
        pot_odds = context.pot_odds
        
        # Calculate position factor (simplified)
        position_factor = 1.1 if position in ["BTN", "CO"] else 0.95 if position in ["SB", "BB"] else 1.0
        
        # Basic decision logic
        if win_prob > 0.65:
            action, confidence = "RAISE", "HIGH"
        elif win_prob > 0.55:
            action, confidence = "CALL", "MEDIUM"
        elif win_prob > pot_odds:
            action, confidence = "CALL", "LOW"
        else:
            action, confidence = "FOLD", "HIGH"
        
        # Calculate expected value
        base_ev = (win_prob * pot_size) - (bet_to_call * (1 - win_prob))
        adjusted_ev = base_ev * position_factor

        return {
            "recommended_action": action,
            "confidence": confidence,
            "win_probability": win_prob,
            "pot_odds": pot_odds,
            "expected_value": adjusted_ev,
            "reasoning": f"Win rate {win_prob:.1%} vs pot odds {pot_odds:.1%}; Position factor: {position_factor:.2f}",
            "position_factor": position_factor,
            "stack_factor": 1.0,  # Simplified
            "implied_odds": 0.0,  # Simplified
            "reverse_implied_odds": 0.0,  # Simplified
            "fold_equity": 0.0,  # Simplified
            "alternative_actions": {
                "FOLD": {"ev": 0.0, "description": "Safe option"},
                "CALL": {"ev": base_ev, "description": "See more cards"},
                "RAISE": {"ev": adjusted_ev * 1.2, "description": "Apply pressure"}
            }
        }

    def _get_hand_description(self, hand_rank: HandRank, values: list[int]) -> str:
        if not values:
            return "Unknown hand"

        if hand_rank == HandRank.HIGH_CARD:
            return f"High card {self._rank_to_string(values[0])}"
        elif hand_rank == HandRank.ONE_PAIR:
            return f"Pair of {self._rank_to_string(values[0])}s"
        elif hand_rank == HandRank.TWO_PAIR:
            if len(values) >= 2:
                return f"Two pair, {self._rank_to_string(values[0])}s and {self._rank_to_string(values[1])}s"
            return "Two pair"
        elif hand_rank == HandRank.THREE_OF_A_KIND:
            return f"Three {self._rank_to_string(values[0])}s"
        elif hand_rank == HandRank.STRAIGHT:
            return f"Straight to {self._rank_to_string(values[0])}"
        elif hand_rank == HandRank.FLUSH:
            return f"Flush, {self._rank_to_string(values[0])} high"
        elif hand_rank == HandRank.FULL_HOUSE:
            if len(values) >= 2:
                return f"Full house, {self._rank_to_string(values[0])}s full of {self._rank_to_string(values[1])}s"
            return "Full house"
        elif hand_rank == HandRank.FOUR_OF_A_KIND:
            return f"Four {self._rank_to_string(values[0])}s"
        elif hand_rank == HandRank.STRAIGHT_FLUSH:
            return f"Straight flush to {self._rank_to_string(values[0])}"
        elif hand_rank == HandRank.ROYAL_FLUSH:
            return "Royal flush"
        else:
            return "Unknown hand"

    def _rank_to_string(self, rank_value: int) -> str:
        rank_names = {
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
            9: "9",
            10: "10",
            11: "Jack",
            12: "Queen",
            13: "King",
            14: "Ace",
        }
        return rank_names.get(rank_value, str(rank_value))

    def _calculate_strength_score(self, hand_rank: HandRank, values: list[int]) -> float:
        base_score = hand_rank.value * 1000
        for i, value in enumerate(values):
            base_score += value * (15 ** (4 - i))
        return base_score / 10000.0

    def _analyze_potential(self, hole_cards: list[Card], community_cards: list[Card]) -> dict:
        # Analyze drawing potential
        all_cards = hole_cards + community_cards
        suits = Counter(card.suit for card in all_cards)
        ranks = [card.rank.value for card in all_cards]

        flush_draw = any(count >= 4 for count in suits.values())
        straight_draw = self._has_straight_potential(ranks)

        return {
            "flush_draw": flush_draw,
            "straight_draw": straight_draw,
            "high_cards": len([r for r in ranks if r >= 11]),
        }

    def _has_straight_potential(self, ranks: list[int]) -> bool:
        unique_ranks = sorted(set(ranks))
        if len(unique_ranks) < 4:
            return False

        # Check for gaps that could be filled
        return any(unique_ranks[i + 3] - unique_ranks[i] <= 4 for i in range(len(unique_ranks) - 3))

    def _get_betting_reasoning(self, action: str, win_prob: float, pot_odds: float) -> str:
        if action == "RAISE":
            return f"Strong hand with {win_prob:.1%} win probability. Value bet recommended."
        elif action == "CALL":
            if win_prob > pot_odds:
                return f"Positive expected value call. Win rate {win_prob:.1%} > pot odds {pot_odds:.1%}"
            else:
                return f"Marginal call with {win_prob:.1%} win probability."
        else:
            return f"Win probability {win_prob:.1%} is below pot odds {pot_odds:.1%}. Fold recommended."

    def calculate_range_vs_range_equity(self, hero_range: str, villain_range: str,
                                      community_cards: list[Card] = None,
                                      num_simulations: int = 10000) -> dict:
        """
        Calculate equity between two hand ranges
        计算两个手牌范围之间的权益
        
        Args:
            hero_range: Hero's range string (e.g. "AA-QQ, AKs")
            villain_range: Villain's range string (e.g. "22+, A2s+") 
            community_cards: Board cards (if any)
            num_simulations: Number of Monte Carlo simulations per matchup
            
        Returns:
            Dictionary with equity results and range information
            
        Examples:
            >>> calc = TexasHoldemCalculator()
            >>> result = calc.calculate_range_vs_range_equity("AA-QQ", "22+,AKs")
            >>> print(f"Hero equity: {result['hero_equity']:.1%}")
        """
        try:
            from range_parser import parse_ranges
        except ImportError:
            return {"error": "Range parser module not available. Please ensure range_parser.py is present."}
        
        if community_cards is None:
            community_cards = []
            
        try:
            # Parse ranges
            hero_hands = parse_ranges(hero_range)
            villain_hands = parse_ranges(villain_range)
            
            # Remove conflicting combinations with community cards
            hero_hands = hero_hands.remove_conflicting(community_cards)
            villain_hands = villain_hands.remove_conflicting(community_cards)
            
            if hero_hands.size() == 0 or villain_hands.size() == 0:
                return {
                    "error": "No valid combinations remain after filtering board cards",
                    "hero_range": hero_range,
                    "villain_range": villain_range,
                    "hero_combos": hero_hands.size(),
                    "villain_combos": villain_hands.size()
                }
            
            # Calculate equity across all range combinations
            total_hero_equity = 0.0
            total_combinations = 0
            
            hero_combos = hero_hands.get_combinations()
            villain_combos = villain_hands.get_combinations()
            
            # Determine simulations per matchup based on range sizes
            total_matchups = len(hero_combos) * len(villain_combos)
            sims_per_matchup = max(100, num_simulations // max(1, total_matchups // 100))
            
            for hero_combo in hero_combos:
                for villain_combo in villain_combos:
                    # Check for card conflicts
                    all_cards = list(hero_combo) + list(villain_combo) + community_cards
                    if len(set(all_cards)) != len(all_cards):
                        continue  # Skip conflicting combinations
                    
                    # Calculate equity for this specific matchup
                    result = self.calculate_win_probability(
                        hole_cards=list(hero_combo),
                        community_cards=community_cards,
                        num_opponents=1,
                        num_simulations=sims_per_matchup
                    )
                    
                    # Calculate hero's equity (wins + half of ties)
                    hero_equity = result['win_probability'] + 0.5 * result['tie_probability']
                    total_hero_equity += hero_equity
                    total_combinations += 1
            
            if total_combinations == 0:
                return {
                    "error": "No valid combination matchups found",
                    "hero_range": hero_range,
                    "villain_range": villain_range,
                    "hero_combos": hero_hands.size(),
                    "villain_combos": villain_hands.size()
                }
            
            # Calculate average equity
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
                "simulations_per_matchup": sims_per_matchup,
                "community_cards": len(community_cards)
            }
            
        except Exception as e:
            return {
                "error": f"Error calculating range vs range equity: {str(e)}",
                "hero_range": hero_range,
                "villain_range": villain_range
            }


def parse_card_string(card_str: str) -> Card:
    """Parse card string like 'As', 'Kh', '10c', '2d' into Card object"""
    card_str = card_str.strip().upper()

    # Extract rank
    if card_str.startswith("10"):
        rank_str = "10"
        suit_str = card_str[2:]
    else:
        rank_str = card_str[0]
        suit_str = card_str[1:]

    # Parse rank
    rank_map = {
        "2": Rank.TWO,
        "3": Rank.THREE,
        "4": Rank.FOUR,
        "5": Rank.FIVE,
        "6": Rank.SIX,
        "7": Rank.SEVEN,
        "8": Rank.EIGHT,
        "9": Rank.NINE,
        "10": Rank.TEN,
        "T": Rank.TEN,
        "J": Rank.JACK,
        "Q": Rank.QUEEN,
        "K": Rank.KING,
        "A": Rank.ACE,
    }

    # Parse suit
    suit_map = {"H": Suit.HEARTS, "D": Suit.DIAMONDS, "C": Suit.CLUBS, "S": Suit.SPADES}

    if rank_str not in rank_map:
        raise ValueError(f"Invalid rank: {rank_str}")
    if suit_str not in suit_map:
        raise ValueError(f"Invalid suit: {suit_str}")

    return Card(rank_map[rank_str], suit_map[suit_str])


def main():
    """Interactive command line interface for the Texas Hold'em calculator"""
    calculator = TexasHoldemCalculator()

    print("🎰 Texas Hold'em Probability Calculator")
    print("德州扑克概率计算器")
    print("=" * 50)
    print("\nCard format: Rank + Suit (e.g., As, Kh, 10c, 2d)")
    print("牌面格式：等级 + 花色 (例如：As=黑桃A, Kh=红桃K, 10c=梅花10, 2d=方块2)")
    print("Suits: s=♠, h=♥, d=♦, c=♣")
    print("花色：s=黑桃, h=红桃, d=方块, c=梅花")

    while True:
        try:
            print("\n" + "=" * 50)

            # Get hole cards
            hole_input = input("\nEnter your hole cards (e.g., 'As Kh'): ").strip()
            if not hole_input:
                print("Goodbye! 再见！")
                break

            hole_cards = [parse_card_string(card) for card in hole_input.split()]
            if len(hole_cards) != 2:
                print("Please enter exactly 2 hole cards / 请输入正好2张底牌")
                continue

            print(f"Your hole cards / 你的底牌: {', '.join(str(card) for card in hole_cards)}")

            # Get community cards (optional)
            community_input = input("Enter community cards (optional, e.g., '2c 3h 4s'): ").strip()
            community_cards = []
            if community_input:
                community_cards = [parse_card_string(card) for card in community_input.split()]
                print(f"Community cards / 公共牌: {', '.join(str(card) for card in community_cards)}")

            # Get number of opponents
            opponents_input = input("Number of opponents (default 1): ").strip()
            num_opponents = int(opponents_input) if opponents_input else 1

            print(f"\n🎯 Calculating probabilities against {num_opponents} opponent(s)...")
            print(f"正在计算对阵 {num_opponents} 个对手的概率...")

            # Calculate probabilities
            prob_result = calculator.calculate_win_probability(hole_cards, community_cards, num_opponents, 10000)

            # Get hand strength
            strength_result = calculator.get_hand_strength(hole_cards, community_cards)

            # Get betting recommendation
            betting_result = calculator.get_betting_recommendation(hole_cards, community_cards, num_opponents)

            # Display results
            print("\n📊 PROBABILITY ANALYSIS / 概率分析")
            print("-" * 30)
            print(f"Win Probability / 胜率: {prob_result['win_probability']:.1%}")
            print(f"Tie Probability / 平局率: {prob_result['tie_probability']:.1%}")
            print(f"Lose Probability / 败率: {prob_result['lose_probability']:.1%}")

            print("\n💪 HAND STRENGTH / 手牌强度")
            print("-" * 30)
            if "hand_rank" in strength_result:
                print(f"Current Hand / 当前手牌: {strength_result.get('description', 'N/A')}")
                if "strength_score" in strength_result:
                    print(f"Strength Score / 强度分数: {strength_result['strength_score']:.2f}")

            print("\n💡 BETTING RECOMMENDATION / 下注建议")
            print("-" * 30)
            print(f"Recommended Action / 建议行动: {betting_result['recommended_action']}")
            print(f"Confidence / 置信度: {betting_result['confidence']}")
            print(f"Expected Value / 期望值: {betting_result['expected_value']:.2f}")
            print(f"Reasoning / 理由: {betting_result['reasoning']}")

        except ValueError as e:
            print(f"Error / 错误: {e}")
            print("Please check your card format / 请检查你的牌面格式")
        except KeyboardInterrupt:
            print("\nGoodbye! 再见！")
            break
        except Exception as e:
            print(f"Unexpected error / 意外错误: {e}")


if __name__ == "__main__":
    main()
