# api/index.py
import os, sys
from flask import Flask, request, jsonify
import json
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import pure calculation functions
from src.api.calculator_service import (
    calculate_poker_probabilities,
    validate_single_card,
    get_preset_scenarios,
    get_player_positions,
    generate_player_list
)

app = Flask(__name__)

# Vercel timeout constraints (max 10 seconds for hobby plan)
VERCEL_TIMEOUT_MS = 9000  # 9 seconds to be safe
MAX_SIMULATIONS_VERCEL = 5000  # Reduced for faster response

@app.route('/')
def index():
    """Main page redirect for Vercel deployment"""
    return jsonify({
        'message': 'Texas Hold\'em Calculator API',
        'version': '2.0.0',
        'endpoints': {
            '/api/calculate': 'POST - Calculate poker probabilities',
            '/api/validate_card': 'POST - Validate card format',
            '/api/presets': 'GET - Get preset scenarios',
            '/api/positions': 'GET - Get player positions',
            '/api/generate_players': 'POST - Generate player list'
        },
        'demo': 'https://texas-holder.vercel.app'
    })

@app.route('/api/calculate', methods=['POST'])
def calculate_probability():
    """
    API endpoint for probability calculation with timeout handling
    概率计算API端点，带超时处理
    """
    start_time = time.time()
    
    try:
        data = request.json or {}
        
        # Extract parameters with defaults
        hole_cards_str = data.get('hole_cards', [])
        community_cards_str = data.get('community_cards', [])
        num_opponents = int(data.get('num_opponents', 1))
        pot_size = float(data.get('pot_size', 100))
        bet_to_call = float(data.get('bet_to_call', 10))
        num_simulations = int(data.get('num_simulations', 3000))  # Reduced default
        player_position = data.get('player_position', 'BB')
        player_actions = data.get('player_actions', [])
        
        # Apply Vercel constraints
        max_sims = min(num_simulations, MAX_SIMULATIONS_VERCEL)
        
        # Estimate if we'll timeout and adjust simulations
        estimated_time_per_sim = 0.001  # Rough estimate: 1ms per simulation
        estimated_total_time = max_sims * estimated_time_per_sim * 1000  # Convert to ms
        
        if estimated_total_time > VERCEL_TIMEOUT_MS:
            max_sims = int(VERCEL_TIMEOUT_MS / (estimated_time_per_sim * 1000))
            max_sims = max(1000, max_sims)  # Minimum 1000 simulations
        
        # Call pure calculation function
        result = calculate_poker_probabilities(
            hole_cards_str=hole_cards_str,
            community_cards_str=community_cards_str,
            num_opponents=num_opponents,
            num_simulations=num_simulations,
            pot_size=pot_size,
            bet_to_call=bet_to_call,
            player_position=player_position,
            player_actions=player_actions,
            max_sims=max_sims,
            timeout_ms=VERCEL_TIMEOUT_MS
        )
        
        # Add execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        result['execution_time_ms'] = round(execution_time, 2)
        result['vercel_optimized'] = True
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'validation_error'
        }), 400
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f'Calculation error: {str(e)}',
            'error_type': 'calculation_error',
            'execution_time_ms': round(execution_time, 2)
        }), 500

@app.route('/api/validate_card', methods=['POST'])
def validate_card():
    """API endpoint to validate card format"""
    try:
        data = request.json or {}
        card_str = data.get('card', '')
        
        result = validate_single_card(card_str)
        return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'error_type': 'system_error'
        }), 500

@app.route('/api/presets')
def get_presets():
    """Get preset scenarios"""
    try:
        presets = get_preset_scenarios()
        return jsonify(presets)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': 'system_error'
        }), 500

@app.route('/api/positions')
def get_positions():
    """Get available player positions"""
    try:
        positions = get_player_positions()
        return jsonify(positions)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': 'system_error'
        }), 500

@app.route('/api/generate_players', methods=['POST'])
def generate_players():
    """Generate player list based on total players and user position"""
    try:
        data = request.json or {}
        total_players = int(data.get('total_players', 6))
        user_position = data.get('user_position', 'BB')
        
        players = generate_player_list(total_players, user_position)
        return jsonify({'players': players})
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': 'system_error'
        }), 500

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'Texas Hold\'em Calculator API',
        'version': '2.0.0'
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5001)