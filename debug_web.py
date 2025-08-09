#!/usr/bin/env python3
"""
Debug version of the web app with simplified interface
调试版网页应用，简化界面
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    """Simple test page"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Texas Hold'em Calculator - Debug</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #1a1a2e; 
            color: white; 
        }
        .container { max-width: 800px; margin: 0 auto; }
        .card-input { 
            padding: 10px; 
            margin: 5px; 
            background: #2c3e50; 
            border: 2px solid #34495e; 
            color: white; 
            border-radius: 5px;
            width: 60px;
            text-align: center;
            font-size: 14px;
        }
        .btn { 
            padding: 10px 20px; 
            background: #3498db; 
            color: white; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px 5px;
        }
        .btn:hover { background: #2980b9; }
        .section { 
            background: #16213e; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 10px; 
        }
        .results { margin-top: 20px; }
        .hidden { display: none; }
        .error { 
            background: #e74c3c; 
            color: white; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 10px 0; 
        }
        .success { 
            background: #27ae60; 
            color: white; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 10px 0; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎰 Texas Hold'em Calculator</h1>
        <p>德州扑克概率计算器 - Debug Version</p>
        
        <div class="section">
            <h3>Your Hole Cards / 你的底牌:</h3>
            <input type="text" id="hole1" class="card-input" placeholder="As" maxlength="3">
            <input type="text" id="hole2" class="card-input" placeholder="Kh" maxlength="3">
        </div>
        
        <div class="section">
            <h3>Community Cards / 公共牌 (Optional):</h3>
            <label>Flop:</label>
            <input type="text" id="flop1" class="card-input" placeholder="2c" maxlength="3">
            <input type="text" id="flop2" class="card-input" placeholder="3h" maxlength="3">
            <input type="text" id="flop3" class="card-input" placeholder="4s" maxlength="3">
            <br><br>
            <label>Turn:</label>
            <input type="text" id="turn" class="card-input" placeholder="5d" maxlength="3">
            <label>River:</label>
            <input type="text" id="river" class="card-input" placeholder="6c" maxlength="3">
        </div>
        
        <div class="section">
            <h3>Settings / 设置:</h3>
            <label>Opponents / 对手: </label>
            <select id="opponents">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
            </select>
            <br><br>
            <label>Pot Size / 底池: </label>
            <input type="number" id="pot" value="100" style="width: 80px; padding: 5px;">
            <label>Bet to Call / 跟注: </label>
            <input type="number" id="bet" value="10" style="width: 80px; padding: 5px;">
        </div>
        
        <div style="text-align: center;">
            <button class="btn" onclick="calculate()">Calculate / 计算</button>
            <button class="btn" onclick="clearAll()" style="background: #e74c3c;">Clear / 清除</button>
        </div>
        
        <div id="loading" class="hidden" style="text-align: center; margin: 20px;">
            <p>🔄 Calculating... / 计算中...</p>
        </div>
        
        <div id="error" class="error hidden"></div>
        <div id="results" class="results hidden"></div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('results').classList.add('hidden');
            document.getElementById('error').classList.add('hidden');
        }
        
        function hideLoading() {
            document.getElementById('loading').classList.add('hidden');
        }
        
        function showError(msg) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = msg;
            errorDiv.classList.remove('hidden');
            hideLoading();
        }
        
        function showResults(data) {
            hideLoading();
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="success">
                    <h3>📊 Results / 结果:</h3>
                    <p><strong>Win Probability / 胜率:</strong> ${(data.probabilities.win_probability * 100).toFixed(1)}%</p>
                    <p><strong>Current Hand / 当前手牌:</strong> ${data.hand_strength.description || 'N/A'}</p>
                    <p><strong>Recommendation / 建议:</strong> ${data.betting_advice.recommended_action}</p>
                    <p><strong>Reasoning / 理由:</strong> ${data.betting_advice.reasoning}</p>
                </div>
            `;
            resultsDiv.classList.remove('hidden');
        }
        
        async function calculate() {
            const hole1 = document.getElementById('hole1').value.trim();
            const hole2 = document.getElementById('hole2').value.trim();
            
            if (!hole1 || !hole2) {
                showError('Please enter both hole cards / 请输入两张底牌');
                return;
            }
            
            const community = [
                document.getElementById('flop1').value.trim(),
                document.getElementById('flop2').value.trim(),
                document.getElementById('flop3').value.trim(),
                document.getElementById('turn').value.trim(),
                document.getElementById('river').value.trim()
            ].filter(card => card);
            
            const requestData = {
                hole_cards: [hole1, hole2],
                community_cards: community,
                num_opponents: parseInt(document.getElementById('opponents').value),
                pot_size: parseFloat(document.getElementById('pot').value),
                bet_to_call: parseFloat(document.getElementById('bet').value),
                num_simulations: 3000
            };
            
            showLoading();
            
            try {
                const response = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showResults(data);
                } else {
                    showError(data.error || 'Calculation failed / 计算失败');
                }
            } catch (error) {
                showError('Network error / 网络错误: ' + error.message);
            }
        }
        
        function clearAll() {
            document.querySelectorAll('.card-input').forEach(input => input.value = '');
            document.getElementById('opponents').value = '1';
            document.getElementById('pot').value = '100';
            document.getElementById('bet').value = '10';
            document.getElementById('results').classList.add('hidden');
            document.getElementById('error').classList.add('hidden');
            document.getElementById('hole1').focus();
        }
        
        // Test that JavaScript is working
        console.log('Debug web app loaded successfully');
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded, ready to use');
        });
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    # Import the calculator API endpoints
    from web_app import calculate_probability
    app.add_url_rule('/api/calculate', 'calculate', calculate_probability, methods=['POST'])
    
    print("🔧 Debug Web Calculator Starting...")
    print("🌐 Open: http://localhost:5001")
    print("This is a simplified version to test functionality")
    print("这是一个简化版本用于测试功能")
    
    app.run(debug=True, host='0.0.0.0', port=5001)