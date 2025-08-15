# Texas Hold'em Probability Calculator / 德州扑克概率计算器

[![Demo](https://img.shields.io/badge/Demo-texas--holder.vercel.app-blue)](https://texas-holder.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🎰 A comprehensive Texas Hold'em poker probability calculator and strategy advisor that helps you make optimal decisions at the poker table.

🎰 一个全面的德州扑克概率计算器和策略顾问，帮助您在牌桌上做出最优决策。

## 🚀 Live Demo / 在线演示

Try it now: **https://texas-holder.vercel.app**

立即试用：**https://texas-holder.vercel.app**

## 📚 Documentation Index / 文档索引

- [Enhanced Features](MONTE_CARLO_CI_FEATURES.md) - Monte Carlo confidence intervals
- [Performance Optimizations](OPTIMIZATION_SUMMARY.md) - Speed improvements and benchmarks  
- [Range Parser](RANGE_PARSER_FEATURES.md) - Hand range analysis
- [EV Calculator](EV_CALCULATOR_FEATURES.md) - Expected value calculations
- [Auto Enumeration](ENUMERATION_AUTO_FEATURES.md) - Exact vs simulation switching
- [Web Deployment](WEB_DEPLOYMENT.md) - Deployment instructions

## Features / 功能特点

### 🎯 Core Features / 核心功能
- **Hand Evaluation / 手牌评估**: Accurate evaluation of poker hands from High Card to Royal Flush
- **Win Probability Calculation / 胜率计算**: Monte Carlo simulation to calculate win probabilities against multiple opponents
- **Betting Strategy Recommendations / 下注策略推荐**: Intelligent betting advice based on pot odds and hand strength
- **Multi-language Support / 多语言支持**: Full Chinese and English interface

### 📊 Advanced Analytics / 高级分析
- **Monte Carlo Simulations / 蒙特卡罗模拟**: Up to 10,000+ simulations for accurate probability estimation
- **Hand Strength Scoring / 手牌强度评分**: Numerical scoring system for hand comparison
- **Drawing Analysis / 听牌分析**: Detection of flush draws, straight draws, and other potential improvements
- **Expected Value Calculations / 期望值计算**: Mathematical analysis of betting decisions

## Quick Start / 快速开始

### Installation / 安装
```bash
# Clone the repository / 克隆仓库
git clone https://github.com/piechiang/Texas-Holder.git
cd Texas-Holder

# For command-line version - no dependencies required
# 命令行版本 - 无需依赖
# For web version - install Flask
# 网页版本 - 安装Flask
pip install -r requirements.txt
```

### Running Options / 运行方式

| Method / 方式 | Command / 命令 | Features / 特性 | Best For / 适用场景 |
|---|---|---|---|
| **🌐 Web (Local)** | `python web_app.py` | Interactive UI, Real-time calc | Development, Local use |
| **⚡ Web (Vercel)** | Deploy to Vercel | Serverless, Auto-scaling | Production, Sharing |
| **💻 CLI Interactive** | `python texas_holdem_calculator.py` | Command-line interface | Quick calculations |
| **📦 CLI Package** | `pip install -e . && texas-holder` | Installed command | System-wide access |

### Usage Options / 使用选项

#### 🌐 Web Interface (Recommended) / 网页界面（推荐）
```bash
python web_app.py
# Open browser to: http://localhost:5000
# 在浏览器中打开: http://localhost:5000
```

**Features / 功能:**
- Interactive card selection / 交互式选牌
- Real-time probability calculation / 实时概率计算
- Visual results with charts / 带图表的可视化结果
- Mobile-friendly design / 移动端友好设计
- Preset scenarios / 预设场景
- Betting recommendations / 下注建议

#### 💻 Interactive Mode / 交互模式
```bash
python texas_holdem_calculator.py
```

Follow the prompts to enter your cards and get instant analysis:

跟随提示输入您的牌并获得即时分析：

```
🎰 Texas Hold'em Probability Calculator
德州扑克概率计算器
==================================================

Card format: Rank + Suit (e.g., As, Kh, 10c, 2d)
牌面格式：等级 + 花色 (例如：As=黑桃A, Kh=红桃K, 10c=梅花10, 2d=方块2)

Enter your hole cards (e.g., 'As Kh'): As Kd
Your hole cards / 你的底牌: A♠, K♦

Enter community cards (optional, e.g., '2c 3h 4s'): Ac 5h 9s
Community cards / 公共牌: A♣, 5♥, 9♠

Number of opponents (default 1): 2

🎯 Calculating probabilities against 2 opponent(s)...
正在计算对阵 2 个对手的概率...

📊 PROBABILITY ANALYSIS / 概率分析
------------------------------
Win Probability / 胜率: 85.2%
Tie Probability / 平局率: 2.1%
Lose Probability / 败率: 12.7%

💪 HAND STRENGTH / 手牌强度
------------------------------
Current Hand / 当前手牌: Pair of Aces
Strength Score / 强度分数: 8.45

💡 BETTING RECOMMENDATION / 下注建议
------------------------------
Recommended Action / 建议行动: RAISE
Confidence / 置信度: HIGH
Expected Value / 期望值: 75.20
Reasoning / 理由: Strong hand with 85.2% win probability. Value bet recommended.
```

#### Programmatic Usage / 编程使用

```python
from texas_holdem_calculator import TexasHoldemCalculator, parse_card_string

# Initialize calculator / 初始化计算器
calculator = TexasHoldemCalculator()

# Parse cards / 解析牌面
hole_cards = [parse_card_string('As'), parse_card_string('Kd')]
community_cards = [parse_card_string('Ac'), parse_card_string('5h'), parse_card_string('9s')]

# Calculate win probability / 计算胜率
prob_result = calculator.calculate_win_probability(
    hole_cards=hole_cards,
    community_cards=community_cards,
    num_opponents=2,
    num_simulations=10000
)

print(f"Win rate: {prob_result['win_probability']:.1%}")

# Get betting recommendation / 获取下注建议
betting_advice = calculator.get_betting_recommendation(
    hole_cards=hole_cards,
    community_cards=community_cards,
    num_opponents=2,
    pot_size=100,
    bet_to_call=20
)

print(f"Recommended action: {betting_advice['recommended_action']}")
```

## Card Format / 牌面格式

### Rank Notation / 等级表示法
- Numbers / 数字: `2, 3, 4, 5, 6, 7, 8, 9, 10`
- Face cards / 人头牌: `J` (Jack/杰克), `Q` (Queen/皇后), `K` (King/国王), `A` (Ace/王牌)

### Suit Notation / 花色表示法
- `s` or `S` = ♠ Spades / 黑桃
- `h` or `H` = ♥ Hearts / 红桃  
- `d` or `D` = ♦ Diamonds / 方块
- `c` or `C` = ♣ Clubs / 梅花

### Examples / 示例
- `As` = Ace of Spades / 黑桃A
- `Kh` = King of Hearts / 红桃K
- `10c` = Ten of Clubs / 梅花10
- `2d` = Two of Diamonds / 方块2

## Hand Rankings / 手牌排名

From strongest to weakest / 从强到弱：

1. **Royal Flush / 皇家同花顺**: A♠ K♠ Q♠ J♠ 10♠
2. **Straight Flush / 同花顺**: 9♥ 8♥ 7♥ 6♥ 5♥
3. **Four of a Kind / 四条**: K♠ K♥ K♦ K♣ A♠
4. **Full House / 葫芦**: A♠ A♥ A♦ K♠ K♥
5. **Flush / 同花**: A♠ J♠ 9♠ 6♠ 4♠
6. **Straight / 顺子**: A♠ K♥ Q♦ J♣ 10♠
7. **Three of a Kind / 三条**: K♠ K♥ K♦ A♠ Q♥
8. **Two Pair / 两对**: A♠ A♥ K♦ K♣ Q♠
9. **One Pair / 一对**: A♠ A♥ K♦ Q♣ J♠
10. **High Card / 高牌**: A♠ K♥ Q♦ J♣ 9♠

## Algorithm Details / 算法详情

### Monte Carlo Simulation / 蒙特卡罗模拟
The calculator uses Monte Carlo simulation to estimate win probabilities:

计算器使用蒙特卡罗模拟来估算胜率：

1. **Card Removal / 移除已知牌**: Removes known cards (hole cards + community cards) from the deck
2. **Random Completion / 随机补全**: Randomly deals remaining community cards and opponent hole cards
3. **Hand Evaluation / 手牌评估**: Evaluates all hands using standard poker rules
4. **Statistical Analysis / 统计分析**: Repeats process thousands of times for accurate probability estimation

### Betting Strategy / 下注策略
The betting recommendations are based on:

下注建议基于以下因素：

- **Win Probability / 胜率**: Calculated through simulation
- **Pot Odds / 底池赔率**: Ratio of bet size to potential winnings
- **Expected Value / 期望值**: Mathematical expectation of the betting decision
- **Hand Strength / 手牌强度**: Current hand ranking and potential improvements

## Example Scenarios / 示例场景

### Scenario 1: Pre-flop with Premium Hand / 场景1：翻牌前的优质手牌
```
Hole Cards: As Ah (Pocket Aces / 口袋对A)
Community: (none)
Opponents: 1

Result:
- Win Probability: ~85%
- Recommendation: RAISE (强烈建议加注)
- Reasoning: Premium pocket pair with high win rate
```

### Scenario 2: Drawing Hand / 场景2：听牌
```
Hole Cards: 9h 8h
Community: 7h 6s 2c
Opponents: 2

Analysis:
- Current Hand: High card 9
- Drawing Potential: Open-ended straight draw + flush draw
- Win Probability: ~45%
- Recommendation: CALL (if pot odds are favorable)
```

### Scenario 3: Made Hand on River / 场景3：河牌成牌
```
Hole Cards: Kc Ks
Community: Kh 4d 4s 2c As
Opponents: 1

Result:
- Current Hand: Full House (Kings full of Fours)
- Win Probability: ~95%
- Recommendation: RAISE/BET
- Reasoning: Very strong made hand, value bet recommended
```

## Advanced Features / 高级功能

### Customizable Simulations / 可定制模拟
```python
# High precision analysis / 高精度分析
result = calculator.calculate_win_probability(
    hole_cards=cards,
    community_cards=flop,
    num_opponents=5,
    num_simulations=50000  # More simulations = higher accuracy
)
```

### Multi-opponent Analysis / 多对手分析
The calculator accurately handles games with multiple opponents, adjusting probabilities based on the increased competition.

计算器准确处理多对手游戏，根据增加的竞争调整概率。

### Hand History Analysis / 手牌历史分析
```python
# Analyze a complete hand / 分析完整手牌
hands = [
    {'stage': 'preflop', 'cards': ['As', 'Ah']},
    {'stage': 'flop', 'cards': ['As', 'Ah', 'Kc', '7d', '2s']},
    {'stage': 'turn', 'cards': ['As', 'Ah', 'Kc', '7d', '2s', '9h']},
    {'stage': 'river', 'cards': ['As', 'Ah', 'Kc', '7d', '2s', '9h', '4c']}
]

for hand in hands:
    # Analysis for each stage
    pass
```

## Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交Pull Request。

### Development Setup / 开发环境设置
```bash
# Clone repository / 克隆仓库
git clone https://github.com/piechiang/Texas-Holder.git
cd Texas-Holder

# Run tests / 运行测试
python -m pytest tests/

# Run interactive mode / 运行交互模式
python texas_holdem_calculator.py
```

## License / 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

该项目在MIT许可证下授权 - 查看LICENSE文件了解详情。

## Disclaimer / 免责声明

This tool is for educational and entertainment purposes only. Gambling involves risk, and you should never gamble more than you can afford to lose. Please gamble responsibly.

此工具仅用于教育和娱乐目的。赌博涉及风险，您不应该赌博超过您能承受的损失。请负责任地游戏。

## Support / 支持

For questions, suggestions, or bug reports, please open an issue on GitHub.

如有问题、建议或错误报告，请在GitHub上开启issue。

---

**Made with ❤️ for poker enthusiasts worldwide**

**为全世界的扑克爱好者用❤️制作**