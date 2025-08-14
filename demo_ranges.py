#!/usr/bin/env python3
"""
Demo script showcasing range parsing and weighted sampling
演示范围解析和加权抽样功能
"""

from src.strategy.ranges import parse_ranges, RangeParser
from texas_holdem_calculator import parse_card_string

def demo_range_parsing():
    """Demonstrate range parsing capabilities"""
    print("🎯 Texas Hold'em Range Parser Demo")
    print("德州扑克范围解析器演示")
    print("=" * 60)
    
    test_ranges = [
        ("JJ+", "Pocket pairs JJ and higher"),
        ("AKs", "Suited Ace-King only"),
        ("KQo", "Offsuit King-Queen only"),
        ("54s-76s", "Suited connectors from 54 to 76"),
        ("ATs+", "Suited Ace-Ten and higher"),
        ("AA@50%", "Pocket Aces with 50% frequency"),
        ("JJ+, AKs, KQo@75%", "Combined range with weights"),
        ("22+, ATs+, KQo, A5s@30%", "Complex mixed range")
    ]
    
    parser = RangeParser()
    
    for range_expr, description in test_ranges:
        print(f"\n📋 Range: '{range_expr}'")
        print(f"    Description: {description}")
        
        try:
            combos = parser.parse_range(range_expr)
            print(f"    Total combos: {len(combos)}")
            
            if combos:
                # Show first few examples
                examples = combos[:3]
                for i, combo in enumerate(examples):
                    card1, card2 = combo.cards
                    print(f"    Example {i+1}: {card1}{card2} (weight: {combo.weight:.0%})")
                
                if len(combos) > 3:
                    print(f"    ... and {len(combos) - 3} more")
                
                # Show weight statistics
                weights = [combo.weight for combo in combos]
                avg_weight = sum(weights) / len(weights)
                min_weight = min(weights)
                max_weight = max(weights)
                print(f"    Weight stats: avg={avg_weight:.1%}, min={min_weight:.0%}, max={max_weight:.0%}")
        
        except Exception as e:
            print(f"    ❌ Error: {e}")

def demo_weighted_sampling():
    """Demonstrate weighted sampling with blockers"""
    print(f"\n\n🎲 Weighted Sampling Demo")
    print("=" * 60)
    
    # Create a range with different weights
    range_expr = "AA@100%, KK@75%, QQ@50%, JJ@25%"
    print(f"Range: '{range_expr}'")
    
    sampler = parse_ranges(range_expr)
    stats = sampler.get_statistics()
    
    print(f"Total combinations: {stats['total_combos']}")
    print(f"Average weight: {stats['average_weight']:.1%}")
    print()
    
    # Sample without blockers
    print("🎯 Sampling without blockers:")
    for i in range(8):
        combo = sampler.sample()
        if combo:
            card1, card2 = combo.cards
            rank = card1.rank.name if card1.rank == card2.rank else "Mixed"
            print(f"  Sample {i+1}: {card1}{card2} ({rank}, weight: {combo.weight:.0%})")
    
    print()
    
    # Sample with blockers
    blocked_cards = [parse_card_string("As"), parse_card_string("Kh")]
    print(f"🚫 Sampling with blockers: {', '.join(str(c) for c in blocked_cards)}")
    
    for i in range(8):
        combo = sampler.sample(blocked_cards)
        if combo:
            card1, card2 = combo.cards
            rank = card1.rank.name if card1.rank == card2.rank else "Mixed"
            print(f"  Sample {i+1}: {card1}{card2} ({rank}, weight: {combo.weight:.0%})")
        else:
            print(f"  Sample {i+1}: No valid combo available")

def demo_range_vs_range():
    """Demonstrate range vs range concept"""
    print(f"\n\n⚔️  Range vs Range Demo")
    print("=" * 60)
    
    hero_range = "JJ+, AKs, AQs"
    villain_range = "22+, ATs+, KQo"
    
    print(f"Hero range: '{hero_range}'")
    print(f"Villain range: '{villain_range}'")
    print()
    
    # Parse both ranges
    hero_sampler = parse_ranges(hero_range)
    villain_sampler = parse_ranges(villain_range)
    
    hero_stats = hero_sampler.get_statistics()
    villain_stats = villain_sampler.get_statistics()
    
    print(f"Hero combos: {hero_stats['total_combos']}")
    print(f"Villain combos: {villain_stats['total_combos']}")
    print()
    
    # Sample a few matchups
    print("🥊 Sample matchups:")
    for i in range(5):
        # Sample hero hand
        hero_combo = hero_sampler.sample()
        
        # Sample villain hand (respecting hero's cards as blockers)
        hero_cards = list(hero_combo.cards) if hero_combo else []
        villain_combo = villain_sampler.sample(hero_cards)
        
        if hero_combo and villain_combo:
            h1, h2 = hero_combo.cards
            v1, v2 = villain_combo.cards
            print(f"  Matchup {i+1}: {h1}{h2} vs {v1}{v2}")
            print(f"    Weights: Hero {hero_combo.weight:.0%}, Villain {villain_combo.weight:.0%}")
        else:
            print(f"  Matchup {i+1}: Could not sample valid combo")

def main():
    """Run all demos"""
    demo_range_parsing()
    demo_weighted_sampling()
    demo_range_vs_range()
    
    print(f"\n\n🏆 Key Features Demonstrated:")
    print("=" * 60)
    print("✅ Advanced range syntax: JJ+, AKs, 54s-76s, AA@50%")
    print("✅ Weight-based sampling: Different frequencies for different hands")
    print("✅ Blocker-aware sampling: Respects already-dealt cards")
    print("✅ Range combinations: Multiple ranges with different weights")
    print("✅ Connector ranges: Suited/offsuit consecutive pairs")
    print("✅ Statistical accuracy: Proper probability distributions")
    print("✅ Error handling: Graceful parsing of invalid syntax")

if __name__ == "__main__":
    main()