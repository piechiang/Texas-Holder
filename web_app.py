#!/usr/bin/env python3
"""
Texas Hold'em Web Calculator
德州扑克网页计算器

A Flask web application for interactive Texas Hold'em probability calculation.
一个用于交互式德州扑克概率计算的Flask网页应用程序。
"""

from flask import Flask, render_template, request, jsonify
import json
from src.api.calculator_service import (
    calculate_poker_probabilities,
    validate_single_card,
    get_preset_scenarios,
    get_player_positions,
    generate_player_list
)

app = Flask(__name__)

@app.route('/')
def index():
    """Main page / 主页面"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate_probability():
    """API endpoint for probability calculation / 概率计算API端点"""
    try:
        data = request.json or {}
        
        # Extract parameters
        hole_cards_str = data.get('hole_cards', [])
        community_cards_str = data.get('community_cards', [])
        num_opponents = int(data.get('num_opponents', 1))
        pot_size = float(data.get('pot_size', 100))
        bet_to_call = float(data.get('bet_to_call', 10))
        num_simulations = int(data.get('num_simulations', 10000))  # Higher default for local
        player_position = data.get('player_position', 'BB')
        player_actions = data.get('player_actions', [])
        
        # Use the pure calculation function
        result = calculate_poker_probabilities(
            hole_cards_str=hole_cards_str,
            community_cards_str=community_cards_str,
            num_opponents=num_opponents,
            num_simulations=num_simulations,
            pot_size=pot_size,
            bet_to_call=bet_to_call,
            player_position=player_position,
            player_actions=player_actions
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'validation_error'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Calculation error / 计算错误: {str(e)}',
            'error_type': 'calculation_error'
        }), 500

@app.route('/api/validate_card', methods=['POST'])
def validate_card():
    """API endpoint to validate card format / 验证牌面格式的API端点"""
    try:
        data = request.json or {}
        card_str = data.get('card', '')
        
        result = validate_single_card(card_str)
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.route('/api/presets')
def get_presets():
    """Get preset scenarios / 获取预设场景"""
    presets = get_preset_scenarios()
    return jsonify(presets)

@app.route('/api/positions')
def get_positions():
    """Get available player positions / 获取可用玩家位置"""
    positions = get_player_positions()
    return jsonify(positions)

@app.route('/api/generate_players', methods=['POST'])
def generate_players():
    """Generate player list based on total players and user position / 根据总人数和用户位置生成玩家列表"""
    try:
        data = request.json or {}
        total_players = int(data.get('total_players', 6))
        user_position = data.get('user_position', 'BB')
        
        players = generate_player_list(total_players, user_position)
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