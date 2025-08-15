"""
Command Line Interface for Texas Hold'em Calculator with Auto Enumeration/MC
德州扑克计算器命令行界面，支持自动枚举/蒙特卡罗切换
"""

import argparse
import json
import sys
from typing import Optional, List, Union
from pathlib import Path

# Add parent directory to path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import parse_card_string, Card
from src.core.equity_result import EquityResult
from src.core.dispatcher import compute_equity


def parse_cards(card_string: str) -> List[Card]:
    """Parse space-separated card string into list of Card objects"""
    if not card_string.strip():
        return []
    return [parse_card_string(card.strip()) for card in card_string.split()]


def parse_opponent_spec(spec: str) -> Union[List[Card], str]:
    """
    Parse opponent specification
    
    Args:
        spec: Either "random" or space-separated cards like "Qh Qs"
        
    Returns:
        Either "random" string or list of Card objects
    """
    spec = spec.strip().lower()
    if spec == "random":
        return "random"
    else:
        try:
            return parse_cards(spec)
        except Exception as e:
            raise ValueError(f"Invalid opponent specification '{spec}': {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="texas-holder",
        description="Texas Hold'em Equity Calculator with Auto Enumeration/MC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-select enumeration vs Monte Carlo
  texas-holder --hero "AsKs" --villains "QhQs" --auto
  
  # Multiple opponents (will use Monte Carlo)
  texas-holder --hero "AhKh" --villains "random,random" --auto
  
  # Force specific method  
  texas-holder --hero "JcJd" --villains "random" --force-mc --ci 0.01
  
  # Exact enumeration for heads-up
  texas-holder --hero "AsAd" --villains "KhKs" --force-enum
  
  # Web interface (local development)
  texas-holder --web
  
  # Interactive mode
  texas-holder --interactive
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--web", action="store_true", help="Start web interface")
    mode_group.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")

    # Hand specification (not required if using web/interactive)
    parser.add_argument("--hero", help="Hero's hole cards (e.g., 'As Ks')")
    parser.add_argument("--villains", help="Villain specs, comma-separated (e.g., 'Qh Qs,random')")
    parser.add_argument("--community", default="", help="Community cards (e.g., '2h 3s 4d')")
    
    # Method selection
    method_group = parser.add_mutually_exclusive_group()
    method_group.add_argument("--auto", action="store_true", help="Auto-select enumeration or Monte Carlo (default)")
    method_group.add_argument("--force-enum", action="store_true", help="Force exact enumeration")
    method_group.add_argument("--force-mc", action="store_true", help="Force Monte Carlo simulation")
    
    # Simulation parameters (for Monte Carlo)
    parser.add_argument("--ci", type=float, default=0.005, help="Target confidence interval half-width (default: 0.005)")
    parser.add_argument("--max-iter", type=int, default=2_000_000, help="Maximum iterations for MC (default: 2,000,000)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--ci-method", choices=["wilson", "normal"], default="wilson", help="CI calculation method")
    
    # Output options
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.web:
        return start_web_interface()
    elif args.interactive:
        return start_interactive_mode()
    
    # For calculation mode, hero and villains are required
    if not args.hero or not args.villains:
        parser.error("--hero and --villains are required for calculation mode")
    
    # Default to auto if no method specified
    if not args.force_enum and not args.force_mc:
        args.auto = True
    
    try:
        # Parse cards
        hero_cards = parse_cards(args.hero)
        if len(hero_cards) != 2:
            raise ValueError("Hero must have exactly 2 cards")
        
        community_cards = parse_cards(args.community)
        
        # Parse villain specifications
        villain_specs_raw = [v.strip() for v in args.villains.split(",")]
        opponent_specs = []
        
        for spec in villain_specs_raw:
            try:
                parsed_spec = parse_opponent_spec(spec)
                opponent_specs.append(parsed_spec)
            except ValueError as e:
                raise ValueError(f"Error parsing villain '{spec}': {e}")
        
        if args.verbose:
            print(f"Hero: {' '.join(str(c) for c in hero_cards)}")
            
            villains_desc = []
            for i, spec in enumerate(opponent_specs):
                if spec == "random":
                    villains_desc.append(f"Villain {i+1}: Random")
                else:
                    villains_desc.append(f"Villain {i+1}: {' '.join(str(c) for c in spec)}")
            
            for desc in villains_desc:
                print(desc)
            
            if community_cards:
                print(f"Board: {' '.join(str(c) for c in community_cards)}")
            
            # Method selection info
            if args.force_enum:
                print("Method: Forced enumeration")
            elif args.force_mc:
                print("Method: Forced Monte Carlo")
            else:
                print("Method: Auto-select")
            
            if not args.force_enum:  # MC parameters only relevant for MC
                print(f"Target CI: ±{args.ci:.3%}")
                print(f"Max iterations: {args.max_iter:,}")
                
            if args.seed:
                print(f"Seed: {args.seed}")
            print()
        
        # Determine method
        if args.force_enum:
            force_method = "enum"
        elif args.force_mc:
            force_method = "mc"
        else:
            force_method = None  # Auto-select
        
        # Compute equity using dispatcher
        result = compute_equity(
            hero_cards=hero_cards,
            opponent_specs=opponent_specs,
            community_cards=community_cards,
            target_ci=args.ci,
            max_iter=args.max_iter,
            seed=args.seed,
            auto=args.auto,
            force_method=force_method,
            verbose=args.verbose
        )
        
        # Output results
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print("🎯 EQUITY ANALYSIS")
            print("=" * 50)
            print(f"Win Probability: {result.p_hat:.1%}")
            
            if result.mode == "ENUM":
                print("Method: Exact Enumeration")
                print(f"Scenarios: {result.n:,}")
            else:
                print("Method: Monte Carlo Simulation")
                print(f"95% Confidence Interval: [{result.ci_low:.1%}, {result.ci_high:.1%}]")
                print(f"CI Half-width: ±{result.ci_radius:.3%}")
                print(f"Samples: {result.n:,}")
                print(f"Early Stopped: {'Yes' if result.stopped_early else 'No'}")
            
            if result.seed is not None:
                print(f"Seed: {result.seed}")
            print()
            
            if result.tie_probability > 0:
                print(f"Tie Probability: {result.tie_probability:.1%}")
                print(f"Lose Probability: {result.lose_probability:.1%}")
    
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def start_web_interface():
    """Start the Flask web interface"""
    try:
        # Import web_app from project root
        import os
        import subprocess
        
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent
        web_app_path = project_root / "web_app.py"
        
        if not web_app_path.exists():
            print("Error: web_app.py not found", file=sys.stderr)
            return 1
        
        print("🎰 Starting Texas Hold'em Web Calculator...")
        print("🌐 Open your browser and go to: http://localhost:8000")
        print("Press Ctrl+C to stop the server\n")
        
        # Run the web app
        os.chdir(project_root)
        subprocess.run([sys.executable, "web_app.py"])
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"Error starting web interface: {e}", file=sys.stderr)
        return 1


def start_interactive_mode():
    """Start the interactive mode"""
    try:
        # Import the existing interactive calculator
        project_root = Path(__file__).parent.parent.parent
        calc_path = project_root / "texas_holdem_calculator.py"
        
        if not calc_path.exists():
            print("Error: texas_holdem_calculator.py not found", file=sys.stderr)
            return 1
        
        print("🎰 Starting Texas Hold'em Interactive Calculator...")
        print("Note: This will run the classic interactive interface\n")
        
        # Run the interactive calculator
        import os
        import subprocess
        
        os.chdir(project_root)
        subprocess.run([sys.executable, "texas_holdem_calculator.py"])
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Interactive mode stopped")
        return 0
    except Exception as e:
        print(f"Error starting interactive mode: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())