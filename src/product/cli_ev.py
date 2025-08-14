"""
Command Line Interface for EV Analysis
EV分析命令行界面
"""

import argparse
import json
import sys
from typing import Optional, List
from pathlib import Path

# Add parent directory to path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import parse_card_string, Card
from src.strategy.ev_calculator import (
    EVCalculator, EVScenario, ActionType, quick_ev_analysis
)
from src.strategy.ranges import parse_ranges


def parse_cards(card_string: str) -> List[Card]:
    """Parse space-separated card string into list of Card objects"""
    if not card_string.strip():
        return []
    return [parse_card_string(card.strip()) for card in card_string.split()]


def main():
    parser = argparse.ArgumentParser(
        description="Texas Hold'em EV Calculator and Break-even Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
EV Analysis Examples:
  # Basic EV analysis with ranges
  python -m src.product.cli_ev --hero-range "AA, KK" --villain-range "22+" --pot-size 100 --bet-to-call 25
  
  # Specific cards vs range
  python -m src.product.cli_ev --hero "As Ah" --villain-range "TT+, AQs+" --pot-size 150 --bet-to-call 50
  
  # With community cards (flop analysis)
  python -m src.product.cli_ev --hero-range "AKs" --villain-range "22+, ATs+" --community "Ah Kh Qc" --pot-size 80 --bet-to-call 40
  
  # Include raise analysis
  python -m src.product.cli_ev --hero-range "JJ+" --villain-range "random" --pot-size 60 --bet-to-call 20 --raise-size 60 --fold-equity 0.3
  
  # Advanced analysis with implied odds
  python -m src.product.cli_ev --hero-range "78s" --villain-range "TT+, ATs+" --pot-size 40 --bet-to-call 15 --implied-odds 2.0 --future-rounds 2

Betting Context Parameters:
  --pot-size AMOUNT          Current pot size in dollars/chips
  --bet-to-call AMOUNT       Amount needed to call
  --stack-size AMOUNT        Hero's remaining stack (default: 500)
  --position POS             Hero's position: UTG, MP, CO, BTN, SB, BB (default: BTN)
  --betting-round ROUND      Current betting round: preflop, flop, turn, river (default: preflop)

Advanced Analysis:
  --raise-size AMOUNT        Amount to raise (enables raise EV calculation)
  --fold-equity PROB         Probability villain folds to raise (0.0-1.0, default: 0.0)
  --implied-odds MULT        Implied odds multiplier for future betting (default: 1.0)
  --future-rounds N          Expected number of future betting rounds (default: 1)
  --opponent-stack-ratio R   Opponent stack size ratio to pot (default: 1.0)

Output Options:
  --json                     Output results as JSON
  --verbose, -v              Detailed analysis output
  --show-breakeven           Show detailed break-even analysis
  --show-kelly               Show Kelly criterion analysis
        """
    )
    
    # Hand specification
    hero_group = parser.add_mutually_exclusive_group(required=True)
    hero_group.add_argument("--hero", help="Hero's specific hole cards (e.g., 'As Ks')")
    hero_group.add_argument("--hero-range", help="Hero's range (e.g., 'JJ+, AKs, KQo@50%')")
    
    villain_group = parser.add_mutually_exclusive_group(required=True)
    villain_group.add_argument("--villain", help="Villain's specific cards (e.g., 'Qh Qs')")
    villain_group.add_argument("--villain-range", help="Villain's range (e.g., 'TT+, ATs+')")
    
    parser.add_argument("--community", default="", help="Community cards (e.g., '2h 3s 4d')")
    
    # Betting context (required)
    parser.add_argument("--pot-size", type=float, required=True, help="Current pot size")
    parser.add_argument("--bet-to-call", type=float, required=True, help="Amount needed to call")
    parser.add_argument("--stack-size", type=float, default=500.0, help="Hero's stack size (default: 500)")
    parser.add_argument("--position", default="BTN", choices=["UTG", "MP", "CO", "BTN", "SB", "BB"], help="Hero's position")
    parser.add_argument("--betting-round", default="preflop", choices=["preflop", "flop", "turn", "river"], help="Current betting round")
    
    # Advanced analysis
    parser.add_argument("--raise-size", type=float, help="Raise amount for raise EV calculation")
    parser.add_argument("--fold-equity", type=float, default=0.0, help="Probability villain folds to raise (0.0-1.0)")
    parser.add_argument("--implied-odds", type=float, default=1.0, help="Implied odds multiplier")
    parser.add_argument("--future-rounds", type=int, default=1, help="Expected future betting rounds")
    parser.add_argument("--opponent-stack-ratio", type=float, default=1.0, help="Opponent stack ratio to pot")
    
    # Simulation parameters
    parser.add_argument("--ci", type=float, default=0.01, help="Target confidence interval (default: 0.01)")
    parser.add_argument("--max-iter", type=int, default=50_000, help="Maximum iterations for MC (default: 50,000)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    # Output options
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--show-breakeven", action="store_true", help="Show detailed break-even analysis")
    parser.add_argument("--show-kelly", action="store_true", help="Show Kelly criterion analysis")
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.fold_equity < 0 or args.fold_equity > 1:
        print("Error: fold-equity must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)
    
    if args.pot_size <= 0 or args.bet_to_call < 0:
        print("Error: pot-size must be positive and bet-to-call must be non-negative", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse hand specifications
        if args.hero:
            hero_spec = parse_cards(args.hero)
            if len(hero_spec) != 2:
                raise ValueError("Hero must have exactly 2 cards")
        else:
            hero_spec = args.hero_range
        
        if args.villain:
            villain_spec = parse_cards(args.villain)
            if len(villain_spec) != 2:
                raise ValueError("Villain must have exactly 2 cards")
        else:
            villain_spec = args.villain_range
        
        community_cards = parse_cards(args.community)
        
        # Create scenario
        scenario = EVScenario(
            hero_range=hero_spec,
            villain_ranges=[villain_spec],
            community_cards=community_cards,
            pot_size=args.pot_size,
            bet_to_call=args.bet_to_call,
            stack_size=args.stack_size,
            position=args.position,
            betting_round=args.betting_round
        )
        
        if args.verbose:
            print("🎯 EV ANALYSIS SCENARIO")
            print("=" * 50)
            print(f"Hero: {format_hand_spec(hero_spec)}")
            print(f"Villain: {format_hand_spec(villain_spec)}")
            if community_cards:
                print(f"Board: {' '.join(str(c) for c in community_cards)}")
            print(f"Pot Size: ${args.pot_size:.0f}")
            print(f"Bet to Call: ${args.bet_to_call:.0f}")
            print(f"Stack Size: ${args.stack_size:.0f}")
            print(f"Position: {args.position}")
            print(f"Betting Round: {args.betting_round}")
            if args.raise_size:
                print(f"Raise Size: ${args.raise_size:.0f}")
                print(f"Fold Equity: {args.fold_equity:.1%}")
            print()
        
        # Calculate EV
        calculator = EVCalculator()
        result = calculator.calculate_ev(
            scenario=scenario,
            raise_size=args.raise_size,
            fold_equity=args.fold_equity,
            implied_odds_multiplier=args.implied_odds,
            target_ci=args.ci,
            max_iter=args.max_iter,
            seed=args.seed,
            verbose=args.verbose
        )
        
        # Output results
        if args.json:
            output = result.to_dict()
            if args.seed:
                output["analysis_params"] = {
                    "seed": args.seed,
                    "max_iterations": args.max_iter,
                    "confidence_interval": args.ci,
                    "raise_size": args.raise_size,
                    "fold_equity": args.fold_equity,
                    "implied_odds": args.implied_odds
                }
            print(json.dumps(output, indent=2))
        else:
            print_analysis_results(result, args)
    
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_hand_spec(spec) -> str:
    """Format hand specification for display"""
    if isinstance(spec, list):
        return " ".join(str(card) for card in spec)
    elif isinstance(spec, str):
        return spec
    else:
        return str(spec)


def print_analysis_results(result, args):
    """Print detailed analysis results"""
    print("🎯 EV ANALYSIS RESULTS")
    print("=" * 50)
    
    # Equity section
    equity = result.equity_result
    print(f"Equity: {equity.p_hat:.1%}")
    if equity.mode == "MC":
        print(f"95% CI: [{equity.ci_low:.1%}, {equity.ci_high:.1%}]")
        print(f"Samples: {equity.n:,}")
    else:
        print(f"Method: Exact enumeration ({equity.n:,} scenarios)")
    print()
    
    # EV Analysis
    print("📊 EXPECTED VALUE ANALYSIS")
    print("-" * 30)
    print(f"EV(Fold): ${result.ev_fold:.2f}")
    print(f"EV(Call): ${result.ev_call:.2f}")
    
    if result.ev_raise is not None:
        print(f"EV(Raise): ${result.ev_raise:.2f}")
    
    if result.ev_all_in is not None:
        print(f"EV(All-in): ${result.ev_all_in:.2f}")
    
    print(f"Best EV: ${result.best_ev:.2f}")
    print()
    
    # Recommendation
    print("🎯 RECOMMENDATION")
    print("-" * 20)
    print(f"Action: {result.recommended_action.value.upper()}")
    print(f"Confidence: {result.confidence_level}")
    print(f"Reasoning: {result.reasoning}")
    print()
    
    # Break-even analysis
    if args.show_breakeven or args.verbose:
        print("⚖️  BREAK-EVEN ANALYSIS")
        print("-" * 25)
        if result.breakeven_analysis:
            ba = result.breakeven_analysis
            print(f"Pot Odds: {ba.pot_odds:.1%}")
            print(f"Required Equity: {ba.required_equity:.1%}")
            print(f"Current Equity: {ba.current_equity:.1%}")
            print(f"Equity Surplus: {ba.equity_surplus:+.1%}")
            print(f"Risk/Reward Ratio: {ba.risk_reward_ratio:.2f}:1")
            
            if ba.implied_odds != ba.pot_odds:
                print(f"Implied Odds: {ba.implied_odds:.1%}")
            
            if ba.future_pot_potential > 0:
                print(f"Future Pot Potential: ${ba.future_pot_potential:.0f}")
            
            print(f"Decision Confidence: {ba.decision_confidence}")
            print(f"Assessment: {ba.recommendation_reason}")
        else:
            print(f"Required Equity: {result.breakeven_equity:.1%}")
            print(f"Current Equity: {result.equity_result.p_hat:.1%}")
            print(f"Equity Surplus: {result.equity_surplus:+.1%}")
        print()
    
    # Kelly analysis
    if args.show_kelly or args.verbose:
        if result.breakeven_analysis and result.breakeven_analysis.kelly_criterion != 0:
            print("📈 KELLY CRITERION ANALYSIS")
            print("-" * 25)
            kelly = result.breakeven_analysis.kelly_criterion
            print(f"Kelly Criterion: {kelly:.3f}")
            
            if kelly > 0:
                print(f"Optimal Bet Size: {kelly*100:.1f}% of bankroll")
                if kelly > 0.25:
                    print("⚠️  Warning: Very aggressive position (>25%)")
                elif kelly > 0.10:
                    print("💪 Strong position (>10%)")
                else:
                    print("👍 Modest positive edge")
            else:
                print("👎 Negative edge - Kelly suggests not betting")
            print()
    
    # Additional context
    if args.verbose:
        print("📋 SCENARIO DETAILS")
        print("-" * 20)
        print(f"Total pot after call: ${result.scenario.total_pot_after_call:.0f}")
        print(f"Pot odds: {result.pot_odds:.1%}")
        if result.scenario.stack_size > result.scenario.bet_to_call:
            print(f"Stack-to-pot ratio: {result.scenario.stack_size / result.scenario.pot_size:.1f}")


if __name__ == "__main__":
    main()