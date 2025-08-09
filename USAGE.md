# Usage Instructions / 使用说明

## Quick Start / 快速开始

### 1. Interactive Mode / 交互模式
```bash
python texas_holdem_calculator.py
```

### 2. Test the System / 测试系统
```bash
python test_calculator.py
```

### 3. Quick Demo / 快速演示
```bash
python quick_demo.py
```

## Card Input Format / 输入格式

### Ranks / 牌面大小
- `2, 3, 4, 5, 6, 7, 8, 9, 10` - Number cards / 数字牌
- `J` - Jack / 杰克
- `Q` - Queen / 皇后  
- `K` - King / 国王
- `A` - Ace / 王牌

### Suits / 花色
- `s` - Spades / 黑桃 ♠
- `h` - Hearts / 红桃 ♥
- `d` - Diamonds / 方块 ♦
- `c` - Clubs / 梅花 ♣

### Examples / 示例
- `As Kh` - Ace of Spades, King of Hearts / 黑桃A，红桃K
- `10c 9d` - Ten of Clubs, Nine of Diamonds / 梅花10，方块9
- `Jh Js` - Jack of Hearts, Jack of Spades / 红桃J，黑桃J

## Sample Session / 示例会话

```
🎰 Texas Hold'em Probability Calculator
德州扑克概率计算器
==================================================

Enter your hole cards (e.g., 'As Kh'): Ac Ah
Your hole cards / 你的底牌: A♣, A♥

Enter community cards (optional, e.g., '2c 3h 4s'): 8s 9h Kd
Community cards / 公共牌: 8♠, 9♥, K♦

Number of opponents (default 1): 2

🎯 Calculating probabilities against 2 opponent(s)...
正在计算对阵 2 个对手的概率...

📊 PROBABILITY ANALYSIS / 概率分析
------------------------------
Win Probability / 胜率: 78.9%
Tie Probability / 平局率: 1.2%
Lose Probability / 败率: 19.9%

💪 HAND STRENGTH / 手牌强度
------------------------------
Current Hand / 当前手牌: Pair of Aces
Strength Score / 强度分数: 8.45

💡 BETTING RECOMMENDATION / 下注建议
------------------------------
Recommended Action / 建议行动: RAISE
Confidence / 置信度: HIGH
Expected Value / 期望值: 65.80
Reasoning / 理由: Strong hand with 78.9% win probability. Value bet recommended.
```

## Key Features / 主要功能

1. **Accurate Hand Evaluation / 准确手牌评估**
   - Recognizes all standard poker hands / 识别所有标准扑克手牌
   - Handles edge cases correctly / 正确处理边缘情况

2. **Monte Carlo Simulation / 蒙特卡罗模拟**  
   - Up to 10,000+ simulations for accuracy / 多达10,000+次模拟确保准确性
   - Configurable simulation count / 可配置模拟次数

3. **Strategic Recommendations / 策略建议**
   - Based on pot odds and hand strength / 基于底池赔率和手牌强度
   - Considers number of opponents / 考虑对手数量

4. **Multi-language Support / 多语言支持**
   - Full Chinese and English interface / 完整中英文界面
   - Clear explanations in both languages / 两种语言的清晰解释

## Tips for Use / 使用提示

1. **Preflop Analysis / 翻牌前分析**
   - Enter only your hole cards / 仅输入底牌
   - Use for starting hand decisions / 用于起手牌决策

2. **Post-flop Analysis / 翻牌后分析** 
   - Include community cards as they're dealt / 包含已发出的公共牌
   - Recalculate after each street / 每轮后重新计算

3. **Opponent Count / 对手数量**
   - More opponents = lower win probability / 对手越多胜率越低
   - Adjust strategy accordingly / 相应调整策略

4. **Pot Odds Consideration / 考虑底池赔率**
   - Follow the recommended actions / 遵循推荐行动
   - Consider position and player types / 考虑位置和玩家类型

## Advanced Usage / 高级使用

### Programmatic Access / 编程访问
```python
from texas_holdem_calculator import TexasHoldemCalculator, parse_card_string

calculator = TexasHoldemCalculator()
hole_cards = [parse_card_string('As'), parse_card_string('Kh')]
prob = calculator.calculate_win_probability(hole_cards, [], 1, 10000)
print(f"Win rate: {prob['win_probability']:.1%}")
```

### Batch Analysis / 批量分析
```python
# Analyze multiple scenarios
scenarios = [
    (['As', 'Ah'], []),  # Pocket Aces
    (['Ks', 'Qh'], []),  # King-Queen
    (['7c', '2d'], [])   # Weak hand
]

for hole_strs, community_strs in scenarios:
    hole_cards = [parse_card_string(c) for c in hole_strs]
    result = calculator.calculate_win_probability(hole_cards, [], 1)
    print(f"{' '.join(hole_strs)}: {result['win_probability']:.1%}")
```

## Troubleshooting / 故障排除

### Common Issues / 常见问题

1. **Invalid Card Format / 无效牌面格式**
   - Use correct format: rank + suit (e.g., 'As', '10h') / 使用正确格式
   - Check spelling of ranks and suits / 检查等级和花色拼写

2. **Duplicate Cards / 重复牌**
   - Ensure no card appears twice / 确保没有重复牌
   - Check hole cards and community cards / 检查底牌和公共牌

3. **Performance Issues / 性能问题**
   - Reduce simulation count for faster results / 减少模拟次数获得更快结果
   - Use 1000-5000 simulations for quick analysis / 快速分析使用1000-5000次模拟

### Getting Help / 获取帮助

- Check the README.md for detailed documentation / 查看README.md获得详细文档
- Run tests to verify installation / 运行测试验证安装
- Review example scenarios / 查看示例场景

---

**Happy Playing! / 游戏愉快！** 🎰