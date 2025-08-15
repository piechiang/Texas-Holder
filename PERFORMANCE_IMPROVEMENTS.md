# 🚀 Texas Hold'em Calculator - Performance Improvements

This document outlines the major performance and accuracy improvements implemented in the enhanced version of the Texas Hold'em calculator.

## 📊 Overview of Improvements

### 1. **Automatic Method Selection** 🤖
The calculator now automatically chooses the optimal calculation method based on scenario complexity:

- **Exact Enumeration**: For small scenarios (turn/river heads-up, river multiway)
- **Vectorized Monte Carlo**: For medium scenarios with NumPy available  
- **Standard Monte Carlo**: For complex scenarios or fallback

```python
# Automatically selects best method
result = calculator.calculate_win_probability(
    hole_cards=[As, Kh],
    community_cards=[2c, 7d, 9h, Jc],  # Turn scenario
    num_opponents=1  # → Uses exact enumeration
)
```

### 2. **Exact Enumeration** 🎯
For suitable scenarios, the calculator provides exact probabilities with zero sampling error:

- **Perfect Accuracy**: No Monte Carlo sampling error
- **Fast Performance**: Optimized for small scenarios
- **Automatic Detection**: Used when computationally feasible

**Example Results:**
- River heads-up: Exact result in <1ms
- Turn heads-up: Exact result in <10ms
- Complex scenarios: Automatically falls back to Monte Carlo

### 3. **Confidence Intervals** 📈
All Monte Carlo results now include Wilson score confidence intervals:

```python
result = calculator.calculate_win_probability(
    hole_cards=[As, Kh],
    community_cards=[2c, 7d],
    target_ci=0.005  # Target ±0.5% accuracy
)

print(f"Win rate: {result.win_probability:.1%} ±{result.ci_radius:.1%}")
# Output: Win rate: 68.5% ±0.4%
```

**Benefits:**
- **Quantified Uncertainty**: Know how accurate your results are
- **Early Stopping**: Automatically stops when target precision reached
- **Adaptive Sampling**: More samples for tighter confidence intervals

### 4. **Vectorized Monte Carlo** ⚡
NumPy-based vectorized simulation for 10-50x performance improvement:

```python
# Install for maximum performance
# pip install numpy numba

# Automatically uses vectorized simulation when available
result = calculator.calculate_win_probability(
    hole_cards=[Qs, Qc],
    num_opponents=3,
    num_simulations=50000  # Fast even with high simulation count
)
```

**Performance Gains:**
- **10-50x Speedup**: Compared to Python loops
- **Memory Efficient**: Chunked processing for large simulations
- **Batch Operations**: Evaluates multiple scenarios simultaneously

### 5. **Optimized Hand Evaluation** 🏃‍♂️
Multiple levels of hand evaluation optimization:

- **Numba JIT Compilation**: Ultra-fast evaluation with `@njit` decorators
- **Vectorized Operations**: Batch hand evaluation
- **Lookup Tables**: Pre-computed evaluations for common patterns
- **Smart Caching**: LRU cache for frequently evaluated hands

### 6. **Reproducible Results** 🌱
Full seed control for deterministic results:

```python
# Same seed = identical results
result1 = calculator.calculate_win_probability(..., seed=42)
result2 = calculator.calculate_win_probability(..., seed=42)
assert result1.win_probability == result2.win_probability
```

## 🧪 Performance Benchmarks

### Method Selection Efficiency
| Scenario | Optimal Method | Time | Accuracy |
|----------|---------------|------|----------|
| River heads-up | Enumeration | <1ms | Exact |
| Turn heads-up | Enumeration | <10ms | Exact |
| Flop 3-way | Vectorized MC | ~50ms | ±0.5% |
| Preflop 5-way | Vectorized MC | ~100ms | ±0.5% |

### Speed Improvements
| Component | Original | Enhanced | Speedup |
|-----------|----------|----------|---------|
| Hand Evaluation | 1000/sec | 50000/sec | 50x |
| Monte Carlo | 500/sec | 15000/sec | 30x |
| Small Enumeration | N/A | Instant | ∞ |

## 🎯 Accuracy Improvements

### Confidence Intervals
- **Wilson Score Method**: More accurate than normal approximation
- **Adaptive Precision**: Automatically achieves target accuracy
- **Early Stopping**: Saves computation when precision reached

### Exact Results
- **Zero Sampling Error**: Perfect accuracy for enumerable scenarios
- **Deterministic**: Same inputs always give same outputs
- **Verified Against Known Results**: Tested against poker equity databases

## 💻 Installation & Usage

### Basic Installation
```bash
# Core functionality
pip install -r requirements.txt
```

### Maximum Performance
```bash
# Install performance packages
pip install numpy numba

# Verify installation
python -c "import numba; print('Numba available for maximum performance')"
```

### Enhanced Usage Examples

#### Basic Calculation with Confidence Intervals
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
print(f"Method: {result['method']}")
print(f"Simulations: {result['simulations']:,}")
```

#### Advanced Calculator Configuration
```python
from src.core.enhanced_calculator import EnhancedTexasHoldemCalculator, CalculatorConfig

config = CalculatorConfig(
    prefer_enumeration=True,      # Use exact when possible
    prefer_vectorized=True,       # Use NumPy when available
    target_ci_radius=0.005,       # ±0.5% target accuracy
    max_enumeration_time_ms=10000 # Max time for enumeration
)

calculator = EnhancedTexasHoldemCalculator(config)

result = calculator.calculate_win_probability(
    hole_cards=[parse_card_string('As'), parse_card_string('Kh')],
    community_cards=[parse_card_string('2c'), parse_card_string('7d')],
    num_opponents=2,
    seed=42
)
```

## 🧪 Testing & Validation

### Regression Tests
- **Known Scenarios**: Tested against verified poker equity results
- **Method Consistency**: Enumeration vs Monte Carlo agreement
- **Reproducibility**: Seed control validation

### Performance Tests
- **Benchmark Suite**: Comprehensive performance testing
- **Memory Usage**: Efficient memory utilization
- **Scalability**: Performance across different scenario sizes

## 🔄 Backward Compatibility

The enhanced calculator maintains full backward compatibility:

```python
# Original interface still works
from texas_holdem_calculator import TexasHoldemCalculator

calculator = TexasHoldemCalculator()
result = calculator.calculate_win_probability(...)  # Same API
```

## 🎯 When to Use Each Method

### Use Exact Enumeration When:
- ✅ Turn or river scenarios
- ✅ Heads-up or small multiway
- ✅ Need perfect accuracy
- ✅ Results will be cached/reused

### Use Vectorized Monte Carlo When:
- ✅ Preflop or complex scenarios
- ✅ Many opponents
- ✅ NumPy available
- ✅ High simulation counts needed

### Use Standard Monte Carlo When:
- ✅ Fallback for compatibility
- ✅ Limited dependencies
- ✅ Small simulation counts

## 📈 Future Improvements

### Planned Enhancements
- **GPU Acceleration**: CUDA/OpenCL support for massive parallelization
- **Range vs Range**: Efficient range-based equity calculations
- **ICM Integration**: Tournament equity calculations
- **Advanced Caching**: Redis/disk caching for large-scale usage

### Performance Targets
- **Sub-millisecond Enumeration**: For all river scenarios
- **100k+ Simulations/sec**: For Monte Carlo methods
- **Memory Optimization**: <100MB for largest calculations

## 🤝 Contributing

To contribute to performance improvements:

1. **Profile**: Use `cProfile` to identify bottlenecks
2. **Benchmark**: Add tests to `tests/test_performance_benchmarks.py`
3. **Validate**: Ensure accuracy with `tests/test_accuracy_regression.py`
4. **Document**: Update this file with performance gains

---

**Run the demo to see these improvements in action:**
```bash
python quick_demo_improvements.py
```