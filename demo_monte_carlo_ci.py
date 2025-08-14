#!/usr/bin/env python3
"""
Demo script showcasing Monte Carlo with 95% confidence intervals and early stopping
演示蒙特卡罗95%置信区间和早停功能
"""

import sys
from src.product.cli import main as cli_main

def run_demo():
    """Run demonstration of new Monte Carlo CI features"""
    
    print("🎰 Texas Hold'em Monte Carlo CI Demo")
    print("德州扑克蒙特卡罗置信区间演示")
    print("=" * 60)
    
    demos = [
        {
            "name": "High-precision AK vs Random (±0.5% CI)",
            "args": ["--hero", "Ah Kh", "--villains", "random", "--ci", "0.005", "--seed", "42", "--verbose"]
        },
        {
            "name": "Pocket Jacks vs 2 Randoms (±1% CI)",
            "args": ["--hero", "Js Jd", "--villains", "random,random", "--ci", "0.01", "--seed", "123", "--verbose"]
        },
        {
            "name": "Flop scenario with early stopping",
            "args": ["--hero", "As Ks", "--villains", "random", "--community", "Kc 7h 2d", "--ci", "0.01", "--seed", "999", "--verbose"]
        },
        {
            "name": "JSON output example",
            "args": ["--hero", "Qh Qd", "--villains", "random", "--ci", "0.02", "--seed", "555", "--json"]
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. {demo['name']}")
        print("-" * len(demo['name']))
        
        # Temporarily replace sys.argv to simulate CLI call
        original_argv = sys.argv[:]
        try:
            sys.argv = ["demo"] + demo['args']
            cli_main()
        except SystemExit:
            pass  # Expected from argparse
        finally:
            sys.argv = original_argv
        
        if i < len(demos):
            print("\n" + "=" * 60)

if __name__ == "__main__":
    run_demo()