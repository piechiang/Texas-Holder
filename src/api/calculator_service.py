"""
Pure function calculator service for API endpoints
纯函数计算器服务，用于API端点

This module provides stateless calculation functions that can be used
by both Flask web app and Vercel serverless functions.
"""

from typing import List, Dict, Any, Optional, Tuple
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from texas_holdem_calculator import TexasHoldemCalculator, parse_card_string
from src.core.exact_enumeration import ExactEnumerator, should_use_enumeration


def validate_cards_input(hole_cards_str: List[str], community_cards_str: List[str]) -> Optional[str]:
    """
    Validate card input format and check for duplicates
    验证牌面输入格式并检查重复
    
    Returns:
        None if valid, error message string if invalid
    """
    # Validate hole cards count
    if len(hole_cards_str) != 2:
        return 'Must provide exactly 2 hole cards / 必须提供正好2张底牌'
    
    # Validate community cards count
    if len(community_cards_str) > 5:
        return 'Cannot have more than 5 community cards / 公共牌不能超过5张'
    
    # Check for duplicates
    all_cards_str = hole_cards_str + community_cards_str
    if len(all_cards_str) != len(set(all_cards_str)):
        return 'Duplicate cards detected / 检测到重复牌'
    
    # Try to parse cards to validate format
    try:
        [parse_card_string(card) for card in hole_cards_str]
        [parse_card_string(card) for card in community_cards_str]
    except ValueError as e:
        return f'Invalid card format / 无效牌面格式: {str(e)}'
    
    return None


def calculate_poker_probabilities(
    hole_cards_str: List[str],
    community_cards_str: List[str],
    num_opponents: int = 1,
    num_simulations: int = 5000,
    pot_size: float = 100.0,
    bet_to_call: float = 10.0,
    player_position: str = 'BB',
    player_actions: List[str] = None,
    max_sims: Optional[int] = None,
    timeout_ms: Optional[int] = None
) -> Dict[str, Any]:
    """
    Pure function to calculate poker probabilities and recommendations
    计算扑克概率和建议的纯函数
    
    Args:
        hole_cards_str: List of hole card strings (e.g., ['As', 'Kh'])
        community_cards_str: List of community card strings
        num_opponents: Number of opponents
        num_simulations: Number of Monte Carlo simulations
        pot_size: Current pot size
        bet_to_call: Amount to call
        player_position: Player's position at table
        player_actions: List of previous actions
        max_sims: Maximum simulations (for timeout handling)
        timeout_ms: Timeout in milliseconds
        
    Returns:
        Dictionary with calculation results
        
    Raises:
        ValueError: If input validation fails
        Exception: If calculation fails
    """
    # Set default player_actions
    if player_actions is None:
        player_actions = []
    
    # Validate input
    error_msg = validate_cards_input(hole_cards_str, community_cards_str)
    if error_msg:
        raise ValueError(error_msg)
    
    # Apply timeout constraints
    if max_sims and num_simulations > max_sims:
        num_simulations = max_sims
    
    # Parse cards
    hole_cards = [parse_card_string(card) for card in hole_cards_str]
    community_cards = [parse_card_string(card) for card in community_cards_str] if community_cards_str else []
    
    # Determine calculation method: exact enumeration vs Monte Carlo
    use_enumeration = should_use_enumeration(
        num_opponents=num_opponents,
        num_community_cards=len(community_cards),
        known_opponents=0  # Assume all opponents are random
    )
    
    calculation_method = "EXACT_ENUM" if use_enumeration else "MONTE_CARLO"
    
    if use_enumeration and num_opponents <= 2:
        # Use exact enumeration for 1v1 or 1v2 scenarios
        try:
            enumerator = ExactEnumerator(use_fast_evaluator=True)
            
            if num_opponents == 1:
                # 1v1 heads-up enumeration
                equity_result = enumerator.enumerate_heads_up(
                    hero_cards=hole_cards,
                    villain_cards=None,  # Random opponent
                    community_cards=community_cards
                )
                prob_result = {
                    'win_probability': equity_result.p_hat,
                    'tie_probability': equity_result.tie_probability,
                    'lose_probability': equity_result.lose_probability,
                    'simulations': equity_result.n
                }
            else:
                # 1v2 multiway enumeration  
                opponent_cards = [None] * num_opponents  # All random opponents
                equity_result = enumerator.enumerate_multiway(
                    hero_cards=hole_cards,
                    opponent_cards=opponent_cards,
                    community_cards=community_cards,
                    max_scenarios=100_000
                )
                prob_result = {
                    'win_probability': equity_result.p_hat,
                    'tie_probability': equity_result.tie_probability,
                    'lose_probability': equity_result.lose_probability,
                    'simulations': equity_result.n
                }
                
        except (ValueError, Exception):
            # Fallback to Monte Carlo if enumeration fails
            calculation_method = "MONTE_CARLO_FALLBACK"
            calculator = TexasHoldemCalculator()
            prob_result = calculator.calculate_win_probability(
                hole_cards=hole_cards,
                community_cards=community_cards,
                num_opponents=num_opponents,
                num_simulations=num_simulations
            )
    else:
        # Use Monte Carlo simulation
        calculator = TexasHoldemCalculator()
        prob_result = calculator.calculate_win_probability(
            hole_cards=hole_cards,
            community_cards=community_cards,
            num_opponents=num_opponents,
            num_simulations=num_simulations
        )
    
    # Get hand strength - create calculator if using enumeration
    if use_enumeration and num_opponents <= 2:
        calculator = TexasHoldemCalculator()  # Need calculator for hand strength and betting
    
    strength_result = calculator.get_hand_strength(hole_cards, community_cards)
    
    # Get betting recommendation
    betting_result = calculator.get_betting_recommendation(
        hole_cards=hole_cards,
        community_cards=community_cards,
        num_opponents=num_opponents,
        pot_size=pot_size,
        bet_to_call=bet_to_call
    )
    
    # Format response with confidence intervals if available
    response = {
        'success': True,
        'calculation_method': calculation_method,
        'probabilities': {
            'win_probability': round(prob_result['win_probability'], 4),
            'tie_probability': round(prob_result['tie_probability'], 4),
            'lose_probability': round(prob_result['lose_probability'], 4),
            'simulations': prob_result['simulations']
        },
        'hand_strength': strength_result,
        'betting_advice': {
            'recommended_action': betting_result['recommended_action'],
            'confidence': betting_result['confidence'],
            'expected_value': round(betting_result['expected_value'], 2),
            'reasoning': betting_result['reasoning'],
            'pot_odds': round(betting_result['pot_odds'], 4)
        },
        'input_summary': {
            'hole_cards': hole_cards_str,
            'community_cards': community_cards_str,
            'num_opponents': num_opponents,
            'pot_size': pot_size,
            'bet_to_call': bet_to_call,
            'player_position': player_position,
            'player_actions': player_actions
        }
    }
    
    # Add confidence interval if available
    if hasattr(prob_result, 'confidence_interval') and prob_result.confidence_interval:
        response['probabilities']['confidence_interval'] = {
            'lower': round(prob_result.confidence_interval[0], 4),
            'upper': round(prob_result.confidence_interval[1], 4),
            'confidence_level': prob_result.confidence_level or 0.95
        }
    
    # Add timeout warning if simulations were reduced
    if max_sims and num_simulations < max_sims:
        response['warnings'] = [
            f'Simulations reduced to {num_simulations} due to timeout constraints'
        ]
    
    return response


def validate_single_card(card_str: str) -> Dict[str, Any]:
    """
    Validate a single card string
    验证单个牌面字符串
    
    Args:
        card_str: Card string to validate
        
    Returns:
        Dictionary with validation result
    """
    try:
        card = parse_card_string(card_str)
        return {
            'valid': True,
            'card': str(card),
            'rank': card.rank.name,
            'suit': card.suit.value
        }
    except ValueError as e:
        return {
            'valid': False,
            'error': str(e)
        }


def get_preset_scenarios() -> Dict[str, Dict[str, Any]]:
    """
    Get predefined poker scenarios
    获取预定义扑克场景
    
    Returns:
        Dictionary of preset scenarios
    """
    return {
        'pocket_aces': {
            'name': 'Pocket Aces / 口袋对A',
            'hole_cards': ['As', 'Ah'],
            'community_cards': [],
            'description': 'Premium starting hand / 顶级起手牌'
        },
        'suited_connectors': {
            'name': 'Suited Connectors / 同花连张',
            'hole_cards': ['9h', '8h'],
            'community_cards': ['7c', '6s', '2d'],
            'description': 'Drawing hand / 听牌'
        },
        'set_on_flop': {
            'name': 'Set on Flop / 翻牌三条',
            'hole_cards': ['8c', '8d'],
            'community_cards': ['8s', 'Kh', '3c'],
            'description': 'Strong made hand / 强成牌'
        },
        'flush_draw': {
            'name': 'Flush Draw / 同花听牌',
            'hole_cards': ['Ah', 'Kh'],
            'community_cards': ['Qh', 'Jh', '2c'],
            'description': 'Strong draw / 强听牌'
        },
        'marginal_hand': {
            'name': 'Marginal Hand / 边际手牌',
            'hole_cards': ['Kc', 'Jd'],
            'community_cards': ['9s', '8h', '3c'],
            'description': 'Difficult decision / 困难决策'
        }
    }


def get_player_positions() -> Dict[str, Dict[str, Any]]:
    """
    Get available player positions
    获取可用玩家位置
    
    Returns:
        Dictionary of player positions
    """
    return {
        'SB': {'name': 'Small Blind / 小盲', 'order': 1},
        'BB': {'name': 'Big Blind / 大盲', 'order': 2},
        'UTG': {'name': 'Under The Gun / 枪口位', 'order': 3},
        'MP': {'name': 'Middle Position / 中位', 'order': 4},
        'CO': {'name': 'Cutoff / 关煞位', 'order': 5},
        'BTN': {'name': 'Button / 按钮位', 'order': 6}
    }


def generate_player_list(total_players: int, user_position: str) -> List[Dict[str, Any]]:
    """
    Generate player list based on total players and user position
    根据总人数和用户位置生成玩家列表
    
    Args:
        total_players: Total number of players
        user_position: User's position
        
    Returns:
        List of player dictionaries
    """
    # Define position order
    position_order = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO', 'HJ', 'EP1', 'EP2']
    position_names = {
        'BTN': 'Button / 按钮位',
        'SB': 'Small Blind / 小盲',
        'BB': 'Big Blind / 大盲',
        'UTG': 'Under The Gun / 枪口位',
        'MP': 'Middle Position / 中位',
        'CO': 'Cutoff / 关煞位',
        'HJ': 'Hijack / 劫持位',
        'EP1': 'Early Position 1 / 早位1',
        'EP2': 'Early Position 2 / 早位2'
    }
    
    # Generate players based on total number
    players = []
    used_positions = position_order[:total_players]
    
    for i, pos in enumerate(used_positions):
        players.append({
            'id': f'player_{i+1}',
            'position': pos,
            'position_name': position_names.get(pos, pos),
            'is_user': pos == user_position,
            'seat': i + 1
        })
    
    return players