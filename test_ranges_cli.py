#!/usr/bin/env python3
"""
Simple test script for range functionality
范围功能简单测试脚本
"""

from src.strategy.ranges import parse_ranges, RangeParser
from texas_holdem_calculator import parse_card_string

def test_basic_parsing():
    """Test basic range parsing"""
    print("🎯 Testing Range Parsing")
    print("=" * 40)
    
    # Test basic range
    sampler = parse_ranges("JJ+, AKs, KQo@75%")
    stats = sampler.get_statistics()
    print(f"Range 'JJ+, AKs, KQo@75%':")
    print(f"  Total combos: {stats['total_combos']}")
    print(f"  Average weight: {stats['average_weight']:.1%}")
    print()
    
    # Test sampling
    print("🎲 Testing Weighted Sampling")
    print("=" * 40)
    
    for i in range(5):
        combo = sampler.sample()
        if combo:
            card1, card2 = combo.cards
            print(f"Sample {i+1}: {card1}{card2} (weight: {combo.weight:.0%})")
    print()
    
    # Test with blockers
    print("🚫 Testing Blocker Logic")
    print("=" * 40)
    
    blocked_cards = [parse_card_string("As"), parse_card_string("Kh")]
    print(f"Blocked cards: {', '.join(str(c) for c in blocked_cards)}")
    
    for i in range(5):
        combo = sampler.sample(blocked_cards)
        if combo:
            card1, card2 = combo.cards
            print(f"Sample {i+1}: {card1}{card2} (no blocked cards)")
        else:
            print(f"Sample {i+1}: No valid combo available")

def test_advanced_syntax():
    """Test advanced range syntax"""
    print("\n🚀 Testing Advanced Syntax")
    print("=" * 40)
    
    test_ranges = [
        "QQ+",          # Plus range
        "54s-76s",      # Dash range  
        "AA@50%",       # Weighted
        "JJ+, AKs, KQo@75%, A5s@30%"  # Combined
    ]
    
    parser = RangeParser()
    
    for range_expr in test_ranges:
        print(f"Range: '{range_expr}'")
        try:
            combos = parser.parse_range(range_expr)
            print(f"  Combos: {len(combos)}")
            if combos:
                print(f"  Example: {combos[0]}")
            print()
        except Exception as e:
            print(f"  Error: {e}")
            print()

if __name__ == "__main__":
    test_basic_parsing()
    test_advanced_syntax()
    print("✅ All range tests completed!")