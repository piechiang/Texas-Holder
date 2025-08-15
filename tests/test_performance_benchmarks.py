"""
Performance benchmarks for poker calculation methods
扑克计算方法的性能基准测试

Comprehensive performance testing across different scenarios and methods
to ensure optimal performance and catch regressions.
跨不同场景和方法的综合性能测试，确保最佳性能并捕获回归。
"""

import time
import statistics
import json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import sys
from pathlib import Path

# Add parent directories to path  
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))

from texas_holdem_calculator import Card, parse_card_string
from src.core.enhanced_calculator import EnhancedTexasHoldemCalculator, CalculatorConfig
from src.core.exact_enumeration import ExactEnumerator
from src.core.numba_evaluator import benchmark_evaluators, NUMBA_AVAILABLE


@dataclass
class BenchmarkResult:
    """Results from a single benchmark test"""
    method: str
    scenario: str
    elapsed_ms: float
    simulations: int
    evaluations_per_second: float
    win_probability: float
    ci_radius: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results"""
    timestamp: str
    system_info: Dict[str, Any]
    results: List[BenchmarkResult]
    summary: Dict[str, Any]


class PerformanceBenchmarks:
    """
    Comprehensive performance benchmarks for poker calculations
    扑克计算的综合性能基准测试
    """
    
    def __init__(self):
        """Initialize benchmark suite"""
        self.scenarios = self._create_test_scenarios()
        self.results: List[BenchmarkResult] = []
    
    def _create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Create diverse test scenarios for benchmarking"""
        return [
            # Preflop scenarios
            {
                'name': 'preflop_heads_up',
                'hero': 'As Kh',
                'board': '',
                'opponents': 1,
                'expected_method': 'enumeration',
                'simulations': 10000
            },
            {
                'name': 'preflop_multiway',
                'hero': 'Qs Qc', 
                'board': '',
                'opponents': 3,
                'expected_method': 'vectorized',
                'simulations': 20000
            },
            
            # Flop scenarios
            {
                'name': 'flop_heads_up',
                'hero': 'As Kh',
                'board': '2c 7d 9h',
                'opponents': 1,
                'expected_method': 'enumeration',
                'simulations': 5000
            },
            {
                'name': 'flop_three_way',
                'hero': '8s 8h',
                'board': '2c 7d 9h',
                'opponents': 2,
                'expected_method': 'vectorized',
                'simulations': 10000
            },
            
            # Turn scenarios
            {
                'name': 'turn_heads_up',
                'hero': 'As Kh',
                'board': '2c 7d 9h Jc',
                'opponents': 1,
                'expected_method': 'enumeration',
                'simulations': 2000
            },
            {
                'name': 'turn_multiway',
                'hero': '7s 6h',
                'board': '5c 4d 9h Jc',
                'opponents': 4,
                'expected_method': 'vectorized',
                'simulations': 15000
            },
            
            # River scenarios
            {
                'name': 'river_heads_up',
                'hero': 'As Kh',
                'board': '2c 7d 9h Jc 4s',
                'opponents': 1,
                'expected_method': 'enumeration',
                'simulations': 1000
            },
            {
                'name': 'river_multiway',
                'hero': '8s 8h',
                'board': '2c 7d 9h Jc 4s',
                'opponents': 3,
                'expected_method': 'enumeration',
                'simulations': 5000
            }
        ]
    
    def benchmark_all_methods(self, runs_per_scenario: int = 3) -> BenchmarkSuite:
        """
        Run comprehensive benchmarks across all methods and scenarios
        跨所有方法和场景运行综合基准测试
        """
        print("Starting comprehensive performance benchmarks...")
        
        # Clear previous results
        self.results = []
        
        # Get system information
        system_info = self._get_system_info()
        
        # Test each scenario with each applicable method
        for scenario in self.scenarios:
            print(f"\nTesting scenario: {scenario['name']}")
            
            hero_cards = [parse_card_string(card) for card in scenario['hero'].split()]
            board_cards = [parse_card_string(card) for card in scenario['board'].split()] if scenario['board'] else []
            
            # Test enumeration (when applicable)
            if self._should_test_enumeration(scenario):
                result = self._benchmark_enumeration(scenario, hero_cards, board_cards, runs_per_scenario)
                if result:
                    self.results.append(result)
            
            # Test vectorized Monte Carlo (when available)
            if self._should_test_vectorized(scenario):
                result = self._benchmark_vectorized_mc(scenario, hero_cards, board_cards, runs_per_scenario)
                if result:
                    self.results.append(result)
            
            # Test standard Monte Carlo
            result = self._benchmark_standard_mc(scenario, hero_cards, board_cards, runs_per_scenario)
            if result:
                self.results.append(result)
            
            # Test enhanced calculator (automatic method selection)
            result = self._benchmark_enhanced_calculator(scenario, hero_cards, board_cards, runs_per_scenario)
            if result:
                self.results.append(result)
        
        # Create summary
        summary = self._create_summary()
        
        # Create benchmark suite
        benchmark_suite = BenchmarkSuite(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            system_info=system_info,
            results=self.results,
            summary=summary
        )
        
        return benchmark_suite
    
    def _should_test_enumeration(self, scenario: Dict[str, Any]) -> bool:
        """Determine if enumeration should be tested for this scenario"""
        # Test enumeration for scenarios likely to be enumerable
        return (scenario['opponents'] <= 2 and 
                len(scenario['board'].split()) >= 3) or scenario['name'].startswith('river')
    
    def _should_test_vectorized(self, scenario: Dict[str, Any]) -> bool:
        """Determine if vectorized MC should be tested"""
        try:
            import numpy as np
            return True
        except ImportError:
            return False
    
    def _benchmark_enumeration(
        self, 
        scenario: Dict[str, Any], 
        hero_cards: List[Card], 
        board_cards: List[Card],
        runs: int
    ) -> Optional[BenchmarkResult]:
        """Benchmark exact enumeration"""
        try:
            enumerator = ExactEnumerator(use_fast_evaluator=True)
            
            # Check if scenario is suitable for enumeration
            if not enumerator.should_use_enumeration(
                num_opponents=scenario['opponents'],
                num_community_cards=len(board_cards)
            ):
                return None
            
            times = []
            results = []
            
            for _ in range(runs):
                start_time = time.perf_counter()
                
                if scenario['opponents'] == 1:
                    result = enumerator.enumerate_heads_up(
                        hero_cards=hero_cards,
                        villain_cards=None,
                        community_cards=board_cards
                    )
                else:
                    opponent_cards = [None] * scenario['opponents']
                    result = enumerator.enumerate_multiway(
                        hero_cards=hero_cards,
                        opponent_cards=opponent_cards,
                        community_cards=board_cards
                    )
                
                end_time = time.perf_counter()
                elapsed_ms = (end_time - start_time) * 1000
                
                times.append(elapsed_ms)
                results.append(result)
            
            # Use median result for consistency
            median_time = statistics.median(times)
            median_result = results[len(results) // 2]
            
            return BenchmarkResult(
                method='enumeration',
                scenario=scenario['name'],
                elapsed_ms=median_time,
                simulations=median_result.n,
                evaluations_per_second=median_result.n / (median_time / 1000) if median_time > 0 else 0,
                win_probability=median_result.p_hat,
                ci_radius=median_result.ci_radius
            )
            
        except Exception as e:
            print(f"Enumeration benchmark failed for {scenario['name']}: {e}")
            return None
    
    def _benchmark_vectorized_mc(
        self,
        scenario: Dict[str, Any],
        hero_cards: List[Card],
        board_cards: List[Card],
        runs: int
    ) -> Optional[BenchmarkResult]:
        """Benchmark vectorized Monte Carlo"""
        try:
            from src.core.vectorized_monte_carlo import simulate_equity_vectorized
            
            times = []
            results = []
            
            for _ in range(runs):
                start_time = time.perf_counter()
                
                result = simulate_equity_vectorized(
                    hero_cards=hero_cards,
                    community_cards=board_cards,
                    num_opponents=scenario['opponents'],
                    num_simulations=scenario['simulations'],
                    seed=42,
                    target_ci=0.005
                )
                
                end_time = time.perf_counter()
                elapsed_ms = (end_time - start_time) * 1000
                
                times.append(elapsed_ms)
                results.append(result)
            
            median_time = statistics.median(times)
            median_result = results[len(results) // 2]
            
            return BenchmarkResult(
                method='vectorized_mc',
                scenario=scenario['name'],
                elapsed_ms=median_time,
                simulations=median_result.n,
                evaluations_per_second=median_result.n / (median_time / 1000) if median_time > 0 else 0,
                win_probability=median_result.p_hat,
                ci_radius=median_result.ci_radius
            )
            
        except Exception as e:
            print(f"Vectorized MC benchmark failed for {scenario['name']}: {e}")
            return None
    
    def _benchmark_standard_mc(
        self,
        scenario: Dict[str, Any],
        hero_cards: List[Card],
        board_cards: List[Card],
        runs: int
    ) -> Optional[BenchmarkResult]:
        """Benchmark standard Monte Carlo"""
        try:
            config = CalculatorConfig(
                prefer_enumeration=False,
                prefer_vectorized=False,
                default_simulations=scenario['simulations']
            )
            calculator = EnhancedTexasHoldemCalculator(config)
            
            times = []
            results = []
            
            for _ in range(runs):
                start_time = time.perf_counter()
                
                result = calculator.calculate_win_probability(
                    hole_cards=hero_cards,
                    community_cards=board_cards,
                    num_opponents=scenario['opponents'],
                    force_method='standard',
                    seed=42
                )
                
                end_time = time.perf_counter()
                elapsed_ms = (end_time - start_time) * 1000
                
                times.append(elapsed_ms)
                results.append(result)
            
            median_time = statistics.median(times)
            median_result = results[len(results) // 2]
            
            return BenchmarkResult(
                method='standard_mc',
                scenario=scenario['name'],
                elapsed_ms=median_time,
                simulations=median_result.simulations,
                evaluations_per_second=median_result.simulations / (median_time / 1000) if median_time > 0 else 0,
                win_probability=median_result.win_probability,
                ci_radius=median_result.ci_radius
            )
            
        except Exception as e:
            print(f"Standard MC benchmark failed for {scenario['name']}: {e}")
            return None
    
    def _benchmark_enhanced_calculator(
        self,
        scenario: Dict[str, Any],
        hero_cards: List[Card],
        board_cards: List[Card],
        runs: int
    ) -> Optional[BenchmarkResult]:
        """Benchmark enhanced calculator with automatic method selection"""
        try:
            config = CalculatorConfig(
                prefer_enumeration=True,
                prefer_vectorized=True,
                default_simulations=scenario['simulations']
            )
            calculator = EnhancedTexasHoldemCalculator(config)
            
            times = []
            results = []
            
            for _ in range(runs):
                start_time = time.perf_counter()
                
                result = calculator.calculate_win_probability(
                    hole_cards=hero_cards,
                    community_cards=board_cards,
                    num_opponents=scenario['opponents'],
                    seed=42
                )
                
                end_time = time.perf_counter()
                elapsed_ms = (end_time - start_time) * 1000
                
                times.append(elapsed_ms)
                results.append(result)
            
            median_time = statistics.median(times)
            median_result = results[len(results) // 2]
            
            return BenchmarkResult(
                method=f'enhanced_{median_result.method}',
                scenario=scenario['name'],
                elapsed_ms=median_time,
                simulations=median_result.simulations,
                evaluations_per_second=median_result.simulations / (median_time / 1000) if median_time > 0 else 0,
                win_probability=median_result.win_probability,
                ci_radius=median_result.ci_radius
            )
            
        except Exception as e:
            print(f"Enhanced calculator benchmark failed for {scenario['name']}: {e}")
            return None
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context"""
        import platform
        
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'machine': platform.machine(),
            'numba_available': NUMBA_AVAILABLE
        }
        
        try:
            import psutil
            system_info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3)
            })
        except ImportError:
            pass
        
        try:
            import numpy as np
            system_info['numpy_version'] = np.__version__
        except ImportError:
            system_info['numpy_version'] = 'not available'
        
        return system_info
    
    def _create_summary(self) -> Dict[str, Any]:
        """Create performance summary from benchmark results"""
        if not self.results:
            return {}
        
        # Group results by method
        method_groups = {}
        for result in self.results:
            method = result.method
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(result)
        
        # Calculate summary statistics
        summary = {
            'total_scenarios': len(set(r.scenario for r in self.results)),
            'total_methods': len(method_groups),
            'methods_tested': list(method_groups.keys())
        }
        
        # Performance comparisons
        method_stats = {}
        for method, results in method_groups.items():
            times = [r.elapsed_ms for r in results]
            speeds = [r.evaluations_per_second for r in results if r.evaluations_per_second > 0]
            
            method_stats[method] = {
                'scenarios_tested': len(results),
                'avg_time_ms': statistics.mean(times),
                'median_time_ms': statistics.median(times),
                'avg_speed_evals_per_sec': statistics.mean(speeds) if speeds else 0,
                'total_simulations': sum(r.simulations for r in results)
            }
        
        summary['method_stats'] = method_stats
        
        # Find fastest method per scenario type
        scenario_best = {}
        for scenario_name in set(r.scenario for r in self.results):
            scenario_results = [r for r in self.results if r.scenario == scenario_name]
            if scenario_results:
                fastest = min(scenario_results, key=lambda x: x.elapsed_ms)
                scenario_best[scenario_name] = {
                    'fastest_method': fastest.method,
                    'time_ms': fastest.elapsed_ms,
                    'speedup_vs_slowest': max(r.elapsed_ms for r in scenario_results) / fastest.elapsed_ms
                }
        
        summary['scenario_best'] = scenario_best
        
        return summary
    
    def save_results(self, benchmark_suite: BenchmarkSuite, filename: str = None):
        """Save benchmark results to JSON file"""
        if filename is None:
            filename = f"benchmark_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to dict for JSON serialization
        data = asdict(benchmark_suite)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Benchmark results saved to {filename}")
    
    def print_summary(self, benchmark_suite: BenchmarkSuite):
        """Print benchmark summary to console"""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        
        print(f"Timestamp: {benchmark_suite.timestamp}")
        print(f"Platform: {benchmark_suite.system_info.get('platform', 'unknown')}")
        print(f"Python: {benchmark_suite.system_info.get('python_version', 'unknown')}")
        print(f"NumPy: {benchmark_suite.system_info.get('numpy_version', 'unknown')}")
        print(f"Numba: {'Available' if benchmark_suite.system_info.get('numba_available') else 'Not Available'}")
        
        summary = benchmark_suite.summary
        print(f"\nScenarios tested: {summary.get('total_scenarios', 0)}")
        print(f"Methods tested: {', '.join(summary.get('methods_tested', []))}")
        
        print("\nMethod Performance:")
        print("-" * 40)
        
        method_stats = summary.get('method_stats', {})
        for method, stats in method_stats.items():
            print(f"{method:20} {stats['avg_time_ms']:8.1f}ms {stats['avg_speed_evals_per_sec']:10.0f} evals/sec")
        
        print("\nFastest Method by Scenario:")
        print("-" * 40)
        
        scenario_best = summary.get('scenario_best', {})
        for scenario, best in scenario_best.items():
            speedup = best['speedup_vs_slowest']
            print(f"{scenario:20} {best['fastest_method']:15} {best['time_ms']:6.1f}ms ({speedup:.1f}x speedup)")


def benchmark_hand_evaluators():
    """Benchmark hand evaluator performance specifically"""
    print("\nBenchmarking hand evaluators...")
    
    results = benchmark_evaluators(num_hands=1000)
    
    print("\nHand Evaluator Performance:")
    print("-" * 50)
    print(f"{'Evaluator':<15} {'Time (s)':<10} {'Hands/sec':<12} {'Speedup':<10}")
    print("-" * 50)
    
    for name, stats in results.items():
        print(f"{name:<15} {stats['elapsed_seconds']:<10.3f} {stats['hands_per_second']:<12.0f} {stats['speedup']:<10.1f}x")
    
    return results


if __name__ == "__main__":
    # Run performance benchmarks
    print("Starting Texas Hold'em Calculator Performance Benchmarks")
    print("=" * 60)
    
    # Initialize benchmark suite
    benchmarks = PerformanceBenchmarks()
    
    # Run comprehensive benchmarks
    suite = benchmarks.benchmark_all_methods(runs_per_scenario=3)
    
    # Print results
    benchmarks.print_summary(suite)
    
    # Benchmark hand evaluators separately
    evaluator_results = benchmark_hand_evaluators()
    
    # Save results
    benchmarks.save_results(suite)
    
    print("\nBenchmark completed successfully!")
    print("Results saved to benchmark_results_*.json")