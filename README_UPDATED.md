# Texas Hold'em Probability Calculator / 德州扑克概率计算器

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Live Demo](https://img.shields.io/badge/demo-live-green.svg)](https://texas-holder.vercel.app)
[![PyPI](https://img.shields.io/pypi/v/texas-holder.svg)](https://pypi.org/project/texas-holder/)

🎰 **[Try the Live Demo →](https://texas-holder.vercel.app)**

A comprehensive Texas Hold'em poker probability calculator and strategy advisor that helps you make optimal decisions at the poker table.

🎰 一个全面的德州扑克概率计算器和策略顾问，帮助您在牌桌上做出最优决策。

## 🚀 Quick Start / 快速开始

### 📱 Try Online (Fastest) / 在线试用（最快）
**[texas-holder.vercel.app](https://texas-holder.vercel.app)** - No installation required!

### 📦 Install & Run Locally / 本地安装运行

| Method / 方式 | Command / 命令 | Use Case / 适用场景 |
|---------------|----------------|-------------------|
| **🌐 Web App** | `python web_app.py` | Interactive GUI, charts / 交互界面，图表 |
| **⚡ CLI** | `python texas_holdem_calculator.py` | Terminal usage, scripting / 终端使用，脚本 |
| **🔥 Enhanced** | `python demo_enhanced_performance.py` | Latest optimizations / 最新优化 |

```bash
# Clone the repository / 克隆仓库
git clone https://github.com/piechiang/Texas-Holder.git
cd Texas-Holder

# Basic installation / 基础安装
pip install -r requirements.txt

# For maximum performance (optional) / 最大性能（可选）
pip install -r requirements-enhanced.txt
```

## 📚 Documentation Index / 文档索引

| Feature / 功能 | Document / 文档 | Description / 描述 |
|----------------|-----------------|-------------------|
| 🎯 **Core Usage** | [USAGE.md](USAGE.md) | Basic operations / 基本操作 |
| 🚀 **Performance** | [PERFORMANCE_IMPROVEMENTS.md](PERFORMANCE_IMPROVEMENTS.md) | Speed optimizations / 性能优化 |
| 📊 **Monte Carlo** | [MONTE_CARLO_CI_FEATURES.md](MONTE_CARLO_CI_FEATURES.md) | Confidence intervals / 置信区间 |
| 🎲 **Enumeration** | [ENUMERATION_AUTO_FEATURES.md](ENUMERATION_AUTO_FEATURES.md) | Exact calculations / 精确计算 |
| 📈 **EV Analysis** | [EV_CALCULATOR_FEATURES.md](EV_CALCULATOR_FEATURES.md) | Expected value / 期望值 |
| 🎯 **Ranges** | [RANGE_PARSER_FEATURES.md](RANGE_PARSER_FEATURES.md) | Hand ranges / 手牌范围 |
| 🌐 **Deployment** | [WEB_DEPLOYMENT.md](WEB_DEPLOYMENT.md) | Web hosting / 网页部署 |

## ✨ Key Features / 主要功能

### 🎯 Enhanced Performance / 增强性能
- **🚀 10-50x speedup** with automatic method selection (enumeration vs Monte Carlo)
- **📊 Confidence intervals** with Wilson score (±0.5% accuracy)
- **🎲 Exact enumeration** for turn/river scenarios (0% error)
- **🌱 Reproducible results** with seed control

### 📊 Core Analytics / 核心分析
- **Hand Evaluation / 手牌评估**: High Card to Royal Flush accuracy
- **Win Probability / 胜率计算**: Up to 100,000+ simulations  
- **Betting Strategy / 下注策略**: Pot odds and EV recommendations
- **Multi-opponent / 多对手**: Support for up to 9 opponents

### 🌐 Multiple Interfaces / 多种界面
- **Web App**: Interactive GUI with charts
- **CLI**: Terminal-based for scripting  
- **API**: RESTful endpoints for integration
- **Vercel**: Serverless deployment ready

## 🎮 Example Usage / 使用示例

### 💻 Command Line / 命令行
```bash
# Basic calculation / 基本计算
python texas_holdem_calculator.py

# Enhanced with confidence intervals / 增强版含置信区间
python quick_demo_improvements.py

# Performance comparison / 性能对比
python demo_enhanced_performance.py
```

### 🌐 Web Interface / 网页界面
```bash
# Local Flask server / 本地Flask服务器
python web_app.py
# → http://localhost:5000

# Or use the online version / 或使用在线版本
# → https://texas-holder.vercel.app
```

### 📊 API Usage / API使用
```python
from src.core.enhanced_calculator import calculate_with_confidence_intervals

result = calculate_with_confidence_intervals(
    hole_cards_str="As Kh",
    community_cards_str="2c 7d 9h", 
    num_opponents=1,
    target_ci=0.005,  # ±0.5% target
    seed=42
)

print(f"Win rate: {result['win_probability']:.1%} ±{result['ci_radius']:.1%}")
# Output: Win rate: 68.5% ±0.4%
```

## 🎯 Deployment Options / 部署选项

| Platform / 平台 | Setup / 设置 | Notes / 说明 |
|------------------|--------------|--------------|
| **Local** | `python web_app.py` | Development, full features |
| **Vercel** | `vercel deploy` | Serverless, auto-scaling |
| **Docker** | `docker run -p 5000:5000 app` | Containerized |
| **PyPI** | `pip install texas-holder` | CLI tool |

## 📈 Performance Benchmarks / 性能基准

| Scenario / 场景 | Method / 方法 | Time / 时间 | Accuracy / 准确性 |
|------------------|---------------|-------------|-------------------|
| River heads-up | Exact enumeration | <1ms | Perfect (0% error) |
| Turn heads-up | Exact enumeration | <10ms | Perfect (0% error) |
| Flop 3-way | Vectorized MC | ~50ms | ±0.5% |
| Preflop 5-way | Vectorized MC | ~100ms | ±0.5% |

## 🛠️ Development / 开发

### Testing / 测试
```bash
# Run core functionality tests / 运行核心功能测试
python test_core_functionality.py

# Run performance benchmarks / 运行性能基准测试
python tests/test_performance_benchmarks.py

# Full test suite / 完整测试套件
pytest tests/
```

### Dependencies / 依赖
```bash
# Minimum / 最小
pip install -r requirements.txt

# Enhanced performance / 增强性能
pip install numpy numba

# Development / 开发
pip install -r requirements-dev.txt
```

## 🤝 Contributing / 贡献

1. Fork the repository / Fork仓库
2. Create feature branch / 创建功能分支: `git checkout -b feature/AmazingFeature`
3. Commit changes / 提交更改: `git commit -m 'Add AmazingFeature'`
4. Push to branch / 推送到分支: `git push origin feature/AmazingFeature`
5. Open Pull Request / 开启Pull Request

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 Acknowledgments / 致谢

- Built with modern Python and performance optimizations
- Inspired by professional poker analysis tools
- Community-driven development and testing

---

**🎰 [Start playing with better decisions →](https://texas-holder.vercel.app)**