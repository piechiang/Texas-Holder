#!/usr/bin/env python3
"""
Demo script showcasing enumeration and automatic method selection
演示枚举和自动方法选择功能
"""

import sys
from src.product.cli import main as cli_main

def run_demo():
    """Run demonstration of enumeration and auto-selection features"""
    
    print("🎯 Texas Hold'em Enumeration & Auto-Selection Demo")
    print("德州扑克枚举与自动选择演示")
    print("=" * 70)
    
    demos = [
        {
            "name": "Auto-selection: Known heads-up on flop (uses ENUMERATION)",
            "args": ["--hero", "As Ad", "--villains", "Kh Ks", "--community", "2c 7h Jd", "--auto", "--verbose"]
        },
        {
            "name": "Auto-selection: Multiple random opponents (uses MONTE CARLO)",
            "args": ["--hero", "As Ad", "--villains", "random,random", "--auto", "--verbose"]
        },
        {
            "name": "Force enumeration: Heads-up known on turn",
            "args": ["--hero", "Js Jd", "--villains", "Ah Kh", "--community", "2c 7h Jd 3s", "--force-enum", "--verbose"]
        },
        {
            "name": "Force Monte Carlo: Same scenario with MC",
            "args": ["--hero", "Js Jd", "--villains", "Ah Kh", "--community", "2c 7h Jd 3s", "--force-mc", "--ci", "0.01", "--seed", "42", "--verbose"]
        },
        {
            "name": "Comparison: ENUM vs MC results (JSON output)",
            "description": "Force enumeration then Monte Carlo for comparison",
            "args": ["--hero", "Qc Qd", "--villains", "As Ks", "--community", "9h 5d 2c", "--force-enum", "--json"]
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. {demo['name']}")
        print("-" * len(demo['name']))
        
        if demo.get('description'):
            print(f"   {demo['description']}")
        
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
            print("\n" + "=" * 70)
    
    print("\n\n🔥 Key Features Demonstrated:")
    print("=" * 40)
    print("✅ Automatic ENUM/MC selection based on scenario complexity")
    print("✅ Exact enumeration for known hands with manageable complexity")
    print("✅ Smart fallback to Monte Carlo for complex scenarios")
    print("✅ Force-method options for specific requirements")
    print("✅ Detailed method reasoning in verbose mode")
    print("✅ Zero confidence intervals for exact enumeration")
    print("✅ Consistent results between ENUM and MC for same scenarios")

if __name__ == "__main__":
    run_demo()