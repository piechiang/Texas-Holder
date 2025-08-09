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

import random
import itertools
from collections import Counter
from enum import Enum
from typing import List, Tuple, Dict, Optional
import json

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
            Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5",
            Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9",
            Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", 
            Rank.KING: "K", Rank.ACE: "A"
        }
        return f"{rank_symbols[self.rank]}{self.suit.value}"
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        random.shuffle(self.cards)
    
    def deal_card(self) -> Card:
        return self.cards.pop()
    
    def remove_cards(self, cards_to_remove: List[Card]):
        for card in cards_to_remove:
            if card in self.cards:
                self.cards.remove(card)

class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")
        
        best_hand = None
        best_rank = HandRank.HIGH_CARD
        best_values = []
        
        for combo in itertools.combinations(cards, 5):
            rank, values = HandEvaluator._evaluate_five_cards(list(combo))
            if rank.value > best_rank.value or (rank == best_rank and values > best_values):
                best_hand = combo
                best_rank = rank
                best_values = values
        
        return best_rank, best_values
    
    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
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
    def _is_straight(ranks: List[int]) -> bool:
        sorted_ranks = sorted(set(ranks))
        if len(sorted_ranks) != 5:
            return False
        
        # Check normal straight
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            return True
        
        # Check A-2-3-4-5 straight (wheel)
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True
        
        return False

class TexasHoldemCalculator:
    def __init__(self):
        self.deck = Deck()
        self.hand_evaluator = HandEvaluator()
    
    def calculate_win_probability(self, hole_cards: List[Card], 
                                community_cards: List[Card] = None,
                                num_opponents: int = 1,
                                num_simulations: int = 10000) -> Dict:
        if community_cards is None:
            community_cards = []
        
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
            
            # Evaluate all hands
            player_hand = hole_cards + sim_community
            player_rank, player_values = self.hand_evaluator.evaluate_hand(player_hand)
            
            player_wins = True
            tie_occurred = False
            
            for opponent_hole in opponent_hands:
                opponent_hand = opponent_hole + sim_community
                opponent_rank, opponent_values = self.hand_evaluator.evaluate_hand(opponent_hand)
                
                if opponent_rank.value > player_rank.value or \
                   (opponent_rank == player_rank and opponent_values > player_values):
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
            'win_probability': win_rate,
            'tie_probability': tie_rate,
            'lose_probability': 1 - win_rate - tie_rate,
            'simulations': total_simulations
        }
    
    def get_hand_strength(self, hole_cards: List[Card], 
                         community_cards: List[Card] = None) -> Dict:
        if community_cards is None:
            community_cards = []
        
        all_cards = hole_cards + community_cards
        if len(all_cards) < 2:
            return {'error': 'Need at least hole cards'}
        
        if len(all_cards) >= 5:
            hand_rank, values = self.hand_evaluator.evaluate_hand(all_cards)
            return {
                'hand_rank': hand_rank.name,
                'hand_value': hand_rank.value,
                'description': self._get_hand_description(hand_rank, values),
                'strength_score': self._calculate_strength_score(hand_rank, values)
            }
        else:
            return {
                'hand_rank': 'INCOMPLETE',
                'description': f'Hole cards: {", ".join(str(card) for card in hole_cards)}',
                'potential': self._analyze_potential(hole_cards, community_cards)
            }
    
    def get_betting_recommendation(self, hole_cards: List[Card],
                                 community_cards: List[Card] = None,
                                 num_opponents: int = 1,
                                 pot_size: float = 100,
                                 bet_to_call: float = 10) -> Dict:
        
        prob_result = self.calculate_win_probability(hole_cards, community_cards, num_opponents, 5000)
        win_prob = prob_result['win_probability']
        
        # Calculate pot odds
        pot_odds = bet_to_call / (pot_size + bet_to_call)
        
        # Basic strategy recommendations
        if win_prob > 0.65:
            action = "RAISE"
            confidence = "HIGH"
        elif win_prob > 0.55:
            action = "CALL"
            confidence = "MEDIUM"
        elif win_prob > pot_odds:
            action = "CALL"
            confidence = "LOW"
        else:
            action = "FOLD"
            confidence = "HIGH"
        
        return {
            'recommended_action': action,
            'confidence': confidence,
            'win_probability': win_prob,
            'pot_odds': pot_odds,
            'expected_value': (win_prob * pot_size) - (bet_to_call * (1 - win_prob)),
            'reasoning': self._get_betting_reasoning(action, win_prob, pot_odds)
        }
    
    def _get_hand_description(self, hand_rank: HandRank, values: List[int]) -> str:
        if not values:
            return "Unknown hand"
        
        if hand_rank == HandRank.HIGH_CARD:
            return f"High card {self._rank_to_string(values[0])}"
        elif hand_rank == HandRank.ONE_PAIR:
            return f"Pair of {self._rank_to_string(values[0])}s"
        elif hand_rank == HandRank.TWO_PAIR:
            if len(values) >= 2:
                return f"Two pair, {self._rank_to_string(values[0])}s and {self._rank_to_string(values[1])}s"
            return f"Two pair"
        elif hand_rank == HandRank.THREE_OF_A_KIND:
            return f"Three {self._rank_to_string(values[0])}s"
        elif hand_rank == HandRank.STRAIGHT:
            return f"Straight to {self._rank_to_string(values[0])}"
        elif hand_rank == HandRank.FLUSH:
            return f"Flush, {self._rank_to_string(values[0])} high"
        elif hand_rank == HandRank.FULL_HOUSE:
            if len(values) >= 2:
                return f"Full house, {self._rank_to_string(values[0])}s full of {self._rank_to_string(values[1])}s"
            return f"Full house"
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
            2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9",
            10: "10", 11: "Jack", 12: "Queen", 13: "King", 14: "Ace"
        }
        return rank_names.get(rank_value, str(rank_value))
    
    def _calculate_strength_score(self, hand_rank: HandRank, values: List[int]) -> float:
        base_score = hand_rank.value * 1000
        for i, value in enumerate(values):
            base_score += value * (15 ** (4 - i))
        return base_score / 10000.0
    
    def _analyze_potential(self, hole_cards: List[Card], community_cards: List[Card]) -> Dict:
        # Analyze drawing potential
        all_cards = hole_cards + community_cards
        suits = Counter(card.suit for card in all_cards)
        ranks = [card.rank.value for card in all_cards]
        
        flush_draw = any(count >= 4 for count in suits.values())
        straight_draw = self._has_straight_potential(ranks)
        
        return {
            'flush_draw': flush_draw,
            'straight_draw': straight_draw,
            'high_cards': len([r for r in ranks if r >= 11])
        }
    
    def _has_straight_potential(self, ranks: List[int]) -> bool:
        unique_ranks = sorted(set(ranks))
        if len(unique_ranks) < 4:
            return False
        
        # Check for gaps that could be filled
        for i in range(len(unique_ranks) - 3):
            if unique_ranks[i + 3] - unique_ranks[i] <= 4:
                return True
        
        return False
    
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

def parse_card_string(card_str: str) -> Card:
    """Parse card string like 'As', 'Kh', '10c', '2d' into Card object"""
    card_str = card_str.strip().upper()
    
    # Extract rank
    if card_str.startswith('10'):
        rank_str = '10'
        suit_str = card_str[2:]
    else:
        rank_str = card_str[0]
        suit_str = card_str[1:]
    
    # Parse rank
    rank_map = {
        '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR, '5': Rank.FIVE,
        '6': Rank.SIX, '7': Rank.SEVEN, '8': Rank.EIGHT, '9': Rank.NINE,
        '10': Rank.TEN, 'J': Rank.JACK, 'Q': Rank.QUEEN, 'K': Rank.KING, 'A': Rank.ACE
    }
    
    # Parse suit
    suit_map = {
        'H': Suit.HEARTS, 'D': Suit.DIAMONDS, 'C': Suit.CLUBS, 'S': Suit.SPADES
    }
    
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
            prob_result = calculator.calculate_win_probability(
                hole_cards, community_cards, num_opponents, 10000
            )
            
            # Get hand strength
            strength_result = calculator.get_hand_strength(hole_cards, community_cards)
            
            # Get betting recommendation
            betting_result = calculator.get_betting_recommendation(
                hole_cards, community_cards, num_opponents
            )
            
            # Display results
            print("\n📊 PROBABILITY ANALYSIS / 概率分析")
            print("-" * 30)
            print(f"Win Probability / 胜率: {prob_result['win_probability']:.1%}")
            print(f"Tie Probability / 平局率: {prob_result['tie_probability']:.1%}")
            print(f"Lose Probability / 败率: {prob_result['lose_probability']:.1%}")
            
            print("\n💪 HAND STRENGTH / 手牌强度")
            print("-" * 30)
            if 'hand_rank' in strength_result:
                print(f"Current Hand / 当前手牌: {strength_result.get('description', 'N/A')}")
                if 'strength_score' in strength_result:
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