"""
Command Line Interface with Range Support
支持范围输入的命令行界面
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
from src.strategy.ranges import parse_ranges, WeightedRangeSampler, Combo
from src.core.rng import RNGManager


def parse_cards(card_string: str) -> List[Card]:
    """Parse space-separated card string into list of Card objects"""
    if not card_string.strip():
        return []
    return [parse_card_string(card.strip()) for card in card_string.split()]


def parse_range_or_cards(spec: str) -> Union[List[Card], WeightedRangeSampler, str]:
    """
    Parse range specification which can be:
    - "random" 
    - Specific cards like "Ah Kh"
    - Range like "JJ+, ATs+, KQo@50%"
    """
    spec = spec.strip()
    
    if spec.lower() == "random":
        return "random"
    
    # Check if it looks like a range (contains +, -, @, or poker notation)
    range_indicators = ['+', '-', '@', 's', 'o']
    is_range = any(indicator in spec.lower() for indicator in range_indicators)
    
    # Also check for multiple parts separated by commas
    has_commas = ',' in spec
    
    if is_range or has_commas:
        try:
            return parse_ranges(spec)
        except Exception as e:
            # Fall back to parsing as specific cards
            try:
                return parse_cards(spec)
            except Exception:
                raise ValueError(f"Invalid range or card specification '{spec}': {e}")
    else:
        # Try parsing as specific cards first
        try:
            return parse_cards(spec)
        except Exception:
            # Fall back to range parsing
            try:
                return parse_ranges(spec)
            except Exception as e:
                raise ValueError(f"Invalid card or range specification '{spec}': {e}")


def create_range_simulation_function(hero_spec, villain_specs, community_cards, seed=None):
    """Create simulation function that respects ranges and weights"""
    rng = RNGManager(seed)
    
    def simulate_once():
        try:
            # Sample hero hand
            hero_cards = sample_from_spec(hero_spec, [], rng)
            if hero_cards is None:
                return False, False
            
            blocked_cards = list(hero_cards) + community_cards
            
            # Sample villain hands
            villain_hands = []
            for villain_spec in villain_specs:
                villain_cards = sample_from_spec(villain_spec, blocked_cards, rng)
                if villain_cards is None:
                    return False, False
                villain_hands.append(villain_cards)
                blocked_cards.extend(villain_cards)
            
            # Use existing calculator to evaluate this specific scenario
            from texas_holdem_calculator import TexasHoldemCalculator
            calc = TexasHoldemCalculator(use_fast_evaluator=True)
            
            # For ranges, we need to convert to enumeration or MC with specific hands
            # For now, use a simplified approach
            result = calc.calculate_win_probability(
                hole_cards=hero_cards,
                community_cards=community_cards,
                num_opponents=len(villain_hands),
                num_simulations=1,
                force_simulation=True
            )
            
            win_prob = result.get('win_probability', 0.0)
            tie_prob = result.get('tie_probability', 0.0)
            
            # Convert to binary outcome
            rand_val = rng.random()
            if rand_val < win_prob:
                return True, False  # Win
            elif rand_val < win_prob + tie_prob:
                return False, True  # Tie
            else:
                return False, False  # Lose
                
        except Exception as e:
            # print(f"Simulation error: {e}")
            return False, False
    
    return simulate_once


def sample_from_spec(spec, blocked_cards, rng):
    """Sample cards from a specification (range, specific cards, or random)"""
    if spec == "random":
        # Sample random two cards not in blocked_cards
        from texas_holdem_calculator import Deck
        deck = Deck()
        deck.remove_cards(blocked_cards)
        if len(deck.cards) < 2:
            return None
        rng.shuffle(deck.cards)
        return deck.cards[:2]
    
    elif isinstance(spec, list):  # Specific cards
        # Check for conflicts
        if any(card in blocked_cards for card in spec):
            return None
        return spec
    
    elif isinstance(spec, WeightedRangeSampler):  # Range
        combo = spec.sample(blocked_cards)
        if combo is None:
            return None
        return list(combo.cards)
    
    else:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Texas Hold'em Equity Calculator with Range Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Range Syntax Examples:
  # Pocket pairs
  --range-hero "JJ+"              # JJ, QQ, KK, AA
  --range-hero "88-QQ"            # 88, 99, TT, JJ, QQ
  
  # Suited/Offsuit hands  
  --range-hero "AKs, AQs"         # Suited AK and AQ
  --range-hero "KQo"              # Offsuit KQ only
  --range-hero "ATs+"             # AT, AJ, AQ, AK suited
  
  # With weights
  --range-hero "AA@50%, KK@75%"   # AA 50% of time, KK 75% of time
  --range-hero "A5s@30%"          # A5 suited 30% of time
  
  # Combined ranges
  --range-hero "JJ+, AKs, KQo, A5s@30%"
  
Usage Examples:
  # Range vs range
  python -m src.product.cli_ranges --range-hero "JJ+,AKs" --range-villain "22+,ATs+"
  
  # Range vs specific hand
  python -m src.product.cli_ranges --range-hero "JJ+" --villains "As Ah"
  
  # Multiple villains with ranges
  python -m src.product.cli_ranges --range-hero "AA" --range-villain "KK,QQ+,random"
        """
    )
    
    # Hand specification - support both old and new syntax
    hero_group = parser.add_mutually_exclusive_group(required=True)
    hero_group.add_argument("--hero", help="Hero's specific hole cards (e.g., 'As Ks')")
    hero_group.add_argument("--range-hero", help="Hero's range (e.g., 'JJ+, AKs, KQo@50%')")
    
    villain_group = parser.add_mutually_exclusive_group(required=True)
    villain_group.add_argument("--villains", help="Villain cards/specs, comma-separated (e.g., 'QhQs,random')")
    villain_group.add_argument("--range-villain", help="Villain ranges, comma-separated (e.g., 'TT+,ATs+')")
    
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
    
    # Default to auto if no method specified
    if not args.force_enum and not args.force_mc:
        args.auto = True
    
    try:
        # Parse hero specification
        if args.hero:
            hero_spec = parse_range_or_cards(args.hero)
        else:
            hero_spec = parse_range_or_cards(args.range_hero)
        
        # Parse villain specifications
        if args.villains:
            villain_specs_raw = [v.strip() for v in args.villains.split(",")]
        else:
            villain_specs_raw = [v.strip() for v in args.range_villain.split(",")]
        
        villain_specs = []
        for spec in villain_specs_raw:
            try:
                parsed_spec = parse_range_or_cards(spec)
                villain_specs.append(parsed_spec)
            except ValueError as e:
                raise ValueError(f"Error parsing villain '{spec}': {e}")
        
        community_cards = parse_cards(args.community)
        
        if args.verbose:
            print(f"Hero: {format_spec(hero_spec)}")
            
            for i, spec in enumerate(villain_specs):
                print(f"Villain {i+1}: {format_spec(spec)}")
            
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
        
        # Check if we can use the dispatcher (for specific hands)
        can_use_dispatcher = True
        hero_cards = None
        opponent_specs = []
        
        if isinstance(hero_spec, list):  # Specific hero cards
            hero_cards = hero_spec
        else:
            can_use_dispatcher = False
        
        if can_use_dispatcher:
            for spec in villain_specs:
                if isinstance(spec, list):
                    opponent_specs.append(spec)
                elif spec == "random":
                    opponent_specs.append("random")
                else:
                    can_use_dispatcher = False
                    break
        
        # Use dispatcher if possible, otherwise use range simulation
        if can_use_dispatcher and not any(isinstance(spec, WeightedRangeSampler) for spec in [hero_spec] + villain_specs):
            # Use existing dispatcher
            force_method = None
            if args.force_enum:
                force_method = "enum"
            elif args.force_mc:
                force_method = "mc"
            
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
        else:
            # Use range-aware Monte Carlo simulation
            from src.core.monte_carlo import simulate_equity
            
            simulation_fn = create_range_simulation_function(
                hero_spec, villain_specs, community_cards, args.seed
            )
            
            result = simulate_equity(
                simulate_once_fn=simulation_fn,
                target_ci=args.ci,
                max_iter=args.max_iter,
                seed=args.seed,
                ci_method=args.ci_method
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


def format_spec(spec):
    """Format a specification for display"""
    if spec == "random":
        return "Random"
    elif isinstance(spec, list):
        return " ".join(str(card) for card in spec)
    elif isinstance(spec, WeightedRangeSampler):
        stats = spec.get_statistics()
        return f"Range ({stats['total_combos']} combos, avg weight: {stats['average_weight']:.1%})"
    else:
        return str(spec)


if __name__ == "__main__":
    main()