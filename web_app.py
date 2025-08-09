#!/usr/bin/env python3
"""
Texas Hold'em Web Calculator
德州扑克网页计算器

A Flask web application for interactive Texas Hold'em probability calculation.
一个用于交互式德州扑克概率计算的Flask网页应用程序。
"""

from flask import Flask, render_template, request, jsonify
import json
from texas_holdem_calculator import TexasHoldemCalculator, parse_card_string

app = Flask(__name__)
calculator = TexasHoldemCalculator()

@app.route('/')
def index():
    """Main page / 主页面"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate_probability():
    """API endpoint for probability calculation / 概率计算API端点"""
    try:
        data = request.json
        
        # Parse input data / 解析输入数据
        hole_cards_str = data.get('hole_cards', [])
        community_cards_str = data.get('community_cards', [])
        num_opponents = int(data.get('num_opponents', 1))
        pot_size = float(data.get('pot_size', 100))
        bet_to_call = float(data.get('bet_to_call', 10))
        num_simulations = int(data.get('num_simulations', 5000))
        player_position = data.get('player_position', 'BB')
        player_actions = data.get('player_actions', [])
        
        # Validate input / 验证输入
        if len(hole_cards_str) != 2:
            return jsonify({'error': 'Must provide exactly 2 hole cards / 必须提供正好2张底牌'}), 400
        
        if len(community_cards_str) > 5:
            return jsonify({'error': 'Cannot have more than 5 community cards / 公共牌不能超过5张'}), 400
        
        # Parse cards / 解析牌面
        try:
            hole_cards = [parse_card_string(card) for card in hole_cards_str]
            community_cards = [parse_card_string(card) for card in community_cards_str] if community_cards_str else []
        except ValueError as e:
            return jsonify({'error': f'Invalid card format / 无效牌面格式: {str(e)}'}), 400
        
        # Check for duplicate cards / 检查重复牌
        all_cards_str = hole_cards_str + community_cards_str
        if len(all_cards_str) != len(set(all_cards_str)):
            return jsonify({'error': 'Duplicate cards detected / 检测到重复牌'}), 400
        
        # Calculate probabilities / 计算概率
        prob_result = calculator.calculate_win_probability(
            hole_cards=hole_cards,
            community_cards=community_cards,
            num_opponents=num_opponents,
            num_simulations=num_simulations
        )
        
        # Get hand strength / 获取手牌强度
        strength_result = calculator.get_hand_strength(hole_cards, community_cards)
        
        # Get betting recommendation / 获取下注建议
        betting_result = calculator.get_betting_recommendation(
            hole_cards=hole_cards,
            community_cards=community_cards,
            num_opponents=num_opponents,
            pot_size=pot_size,
            bet_to_call=bet_to_call
        )
        
        # Format response / 格式化响应
        response = {
            'success': True,
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
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Calculation error / 计算错误: {str(e)}'}), 500

@app.route('/api/validate_card', methods=['POST'])
def validate_card():
    """API endpoint to validate card format / 验证牌面格式的API端点"""
    try:
        data = request.json
        card_str = data.get('card', '')
        
        try:
            card = parse_card_string(card_str)
            return jsonify({
                'valid': True,
                'card': str(card),
                'rank': card.rank.name,
                'suit': card.suit.value
            })
        except ValueError as e:
            return jsonify({
                'valid': False,
                'error': str(e)
            })
            
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/api/presets')
def get_presets():
    """Get preset scenarios / 获取预设场景"""
    presets = {
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
    
    return jsonify(presets)

@app.route('/api/positions')
def get_positions():
    """Get available player positions / 获取可用玩家位置"""
    positions = {
        'SB': {'name': 'Small Blind / 小盲', 'order': 1},
        'BB': {'name': 'Big Blind / 大盲', 'order': 2},
        'UTG': {'name': 'Under The Gun / 枪口位', 'order': 3},
        'MP': {'name': 'Middle Position / 中位', 'order': 4},
        'CO': {'name': 'Cutoff / 关煞位', 'order': 5},
        'BTN': {'name': 'Button / 按钮位', 'order': 6}
    }
    return jsonify(positions)

@app.route('/api/generate_players', methods=['POST'])
def generate_players():
    """Generate player list based on total players and user position / 根据总人数和用户位置生成玩家列表"""
    try:
        data = request.json
        total_players = int(data.get('total_players', 6))
        user_position = data.get('user_position', 'BB')
        
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
        
        return jsonify({'players': players})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🎰 Starting Texas Hold'em Web Calculator...")
    print("🌐 Open your browser and go to: http://localhost:8000")
    print("📱 The web interface supports mobile devices")
    print("\n🎯 Features:")
    print("- Interactive card selection / 交互式选牌")
    print("- Real-time probability calculation / 实时概率计算")
    print("- Betting recommendations / 下注建议")
    print("- Preset scenarios / 预设场景")
    print("- Mobile-friendly design / 移动端友好设计")
    
    app.run(debug=True, host='0.0.0.0', port=8000)