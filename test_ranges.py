"""
Tests for range parser and weighted sampling
范围解析器和加权抽样测试
"""

import pytest
from collections import Counter
import sys
from pathlib import Path

# Add parent directory to import modules
sys.path.append(str(Path(__file__).parent))

from texas_holdem_calculator import parse_card_string
from src.strategy.ranges import RangeParser, WeightedRangeSampler, Combo, parse_ranges
from src.core.rng import RNGManager


def test_range_parse_syntax():
    """Test parsing of various range syntax elements"""
    parser = RangeParser()
    
    # Test exact hands
    combos = parser.parse_range("AA")
    assert len(combos) == 6, "AA should have 6 combinations"
    assert all(combo.weight == 1.0 for combo in combos), "Default weight should be 1.0"
    
    # Test suited hands
    combos = parser.parse_range("AKs")
    assert len(combos) == 4, "AKs should have 4 combinations"
    
    # Test offsuit hands
    combos = parser.parse_range("AKo")
    assert len(combos) == 12, "AKo should have 12 combinations"
    
    # Test plus ranges
    combos = parser.parse_range("QQ+")
    expected_pairs = 3 * 6  # QQ, KK, AA each with 6 combos
    assert len(combos) == expected_pairs, f"QQ+ should have {expected_pairs} combinations"
    
    # Test weighted hands
    combos = parser.parse_range("AA@50%")
    assert len(combos) == 6, "AA@50% should have 6 combinations"
    assert all(combo.weight == 0.5 for combo in combos), "Weight should be 0.5"
    
    # Test combined ranges
    combos = parser.parse_range("AA, KK@75%, AKs")
    aa_combos = [c for c in combos if c.cards[0].rank.name == 'ACE' and c.cards[1].rank.name == 'ACE']
    kk_combos = [c for c in combos if c.cards[0].rank.name == 'KING' and c.cards[1].rank.name == 'KING']
    aks_combos = [c for c in combos if (
        (c.cards[0].rank.name == 'ACE' and c.cards[1].rank.name == 'KING') or
        (c.cards[0].rank.name == 'KING' and c.cards[1].rank.name == 'ACE')
    ) and c.cards[0].suit == c.cards[1].suit]
    
    assert len(aa_combos) == 6, "Should have 6 AA combinations"
    assert len(kk_combos) == 6, "Should have 6 KK combinations"
    assert len(aks_combos) == 4, "Should have 4 AKs combinations"
    assert all(c.weight == 1.0 for c in aa_combos), "AA should have weight 1.0"
    assert all(c.weight == 0.75 for c in kk_combos), "KK should have weight 0.75"


def test_weighted_sampling_distribution():
    """Test that weighted sampling follows the expected distribution"""
    # Create a simple range with different weights
    parser = RangeParser()
    combos = parser.parse_range("AA@100%, KK@50%, QQ@25%")
    
    sampler = WeightedRangeSampler(combos, rng=RNGManager(seed=42))
    
    # Sample many times and check distribution
    num_samples = 10000
    samples = []
    for _ in range(num_samples):
        combo = sampler.sample()
        if combo:
            # Identify the hand type
            rank1 = combo.cards[0].rank.name
            rank2 = combo.cards[1].rank.name
            if rank1 == rank2:
                samples.append(rank1)
    
    counter = Counter(samples)
    total = sum(counter.values())
    
    # Calculate observed frequencies
    aa_freq = counter.get('ACE', 0) / total
    kk_freq = counter.get('KING', 0) / total
    qq_freq = counter.get('QUEEN', 0) / total
    
    # Expected frequencies (normalized)
    # AA: 6 combos * 1.0 weight = 6
    # KK: 6 combos * 0.5 weight = 3  
    # QQ: 6 combos * 0.25 weight = 1.5
    # Total: 10.5
    expected_aa = 6.0 / 10.5
    expected_kk = 3.0 / 10.5
    expected_qq = 1.5 / 10.5
    
    # Allow for some statistical variance (±5%)
    assert abs(aa_freq - expected_aa) < 0.05, f"AA frequency {aa_freq:.3f} should be ~{expected_aa:.3f}"
    assert abs(kk_freq - expected_kk) < 0.05, f"KK frequency {kk_freq:.3f} should be ~{expected_kk:.3f}"
    assert abs(qq_freq - expected_qq) < 0.05, f"QQ frequency {qq_freq:.3f} should be ~{expected_qq:.3f}"


def test_blockers_respected():
    """Test that blocker cards are properly respected in sampling"""
    parser = RangeParser()
    combos = parser.parse_range("AA, KK, QQ")
    
    sampler = WeightedRangeSampler(combos, rng=RNGManager(seed=123))
    
    # Block one Ace
    ace_of_spades = parse_card_string("As")
    blocked_cards = [ace_of_spades]
    
    # Sample many times
    samples = []
    for _ in range(1000):
        combo = sampler.sample(blocked_cards)
        if combo:
            samples.append(combo)
    
    # Check that no sampled combo contains the blocked card
    for combo in samples:
        assert ace_of_spades not in combo.cards, f"Sampled combo {combo} contains blocked card {ace_of_spades}"
    
    # Check that AA combinations are reduced (should only have 3 instead of 6)
    aa_samples = [s for s in samples if s.cards[0].rank.name == 'ACE' and s.cards[1].rank.name == 'ACE']
    
    # With As blocked, only 3 AA combinations possible: Ad-Ah, Ad-Ac, Ah-Ac
    unique_aa = set()
    for combo in aa_samples:
        card_pair = tuple(sorted([str(combo.cards[0]), str(combo.cards[1])]))
        unique_aa.add(card_pair)
    
    # Should be exactly 3 unique AA combinations
    assert len(unique_aa) <= 3, f"With As blocked, should have ≤3 AA combinations, got {len(unique_aa)}"
    
    # More importantly, no combination should contain As
    for combo in aa_samples:
        assert all(str(card) != "A♠" for card in combo.cards), "No AA combo should contain As"


def test_range_dash_syntax():
    """Test dash range syntax like 54s-76s"""
    parser = RangeParser()
    
    # Test suited connectors range
    combos = parser.parse_range("54s-76s")
    
    # Should include: 54s, 65s, 76s (3 types * 4 combinations each = 12)
    expected_count = 3 * 4
    assert len(combos) == expected_count, f"54s-76s should have {expected_count} combinations, got {len(combos)}"
    
    # Check that all are suited
    for combo in combos:
        assert combo.cards[0].suit == combo.cards[1].suit, f"Combo {combo} should be suited"
    
    # Check specific hands are included
    hand_types = set()
    for combo in combos:
        ranks = sorted([combo.cards[0].rank.value, combo.cards[1].rank.value])
        hand_types.add(tuple(ranks))
    
    expected_hands = {(4, 5), (5, 6), (6, 7)}  # 54, 65, 76
    assert hand_types == expected_hands, f"Expected hands {expected_hands}, got {hand_types}"


def test_range_plus_syntax():
    """Test plus range syntax like ATs+"""
    parser = RangeParser()
    
    # Test suited Broadway+ range
    combos = parser.parse_range("ATs+")
    
    # Should include: ATs, AJs, AQs, AKs (4 types * 4 combinations each = 16)
    expected_count = 4 * 4
    assert len(combos) == expected_count, f"ATs+ should have {expected_count} combinations, got {len(combos)}"
    
    # Check that all are suited and involve Ace
    for combo in combos:
        assert combo.cards[0].suit == combo.cards[1].suit, f"Combo {combo} should be suited"
        has_ace = any(card.rank.name == 'ACE' for card in combo.cards)
        assert has_ace, f"Combo {combo} should contain an Ace"
    
    # Check specific hands are included
    hand_types = set()
    for combo in combos:
        ranks = [card.rank.value for card in combo.cards]
        non_ace_rank = min(ranks)  # The non-ace rank
        hand_types.add(non_ace_rank)
    
    expected_ranks = {10, 11, 12, 13}  # T, J, Q, K
    assert hand_types == expected_ranks, f"Expected ranks {expected_ranks}, got {hand_types}"


def test_parse_ranges_convenience_function():
    """Test the convenience function parse_ranges"""
    sampler = parse_ranges("JJ+, AKs, KQo@75%")
    
    assert isinstance(sampler, WeightedRangeSampler), "Should return WeightedRangeSampler"
    
    stats = sampler.get_statistics()
    assert stats['total_combos'] > 0, "Should have some combinations"
    assert 0 < stats['average_weight'] <= 1.0, "Average weight should be between 0 and 1"
    
    # Test sampling works
    combo = sampler.sample()
    assert combo is not None, "Should be able to sample a combo"
    assert isinstance(combo, Combo), "Should return a Combo object"


def test_weight_normalization_and_merging():
    """Test that weights are properly normalized and duplicate combos are merged"""
    parser = RangeParser()
    
    # Test overlapping ranges with different weights
    combos = parser.parse_range("AA@50%, AA@30%")
    
    # Should merge to single AA with combined weight (but capped at 100%)
    assert len(combos) == 6, "Should have 6 AA combinations"
    for combo in combos:
        assert combo.weight == 0.8, f"Merged weight should be 0.5 + 0.3 = 0.8, got {combo.weight}"
    
    # Test weight capping at 1.0
    combos = parser.parse_range("KK@60%, KK@50%")
    assert len(combos) == 6, "Should have 6 KK combinations"
    for combo in combos:
        assert combo.weight == 1.0, f"Weight should be capped at 1.0, got {combo.weight}"


def test_multiple_sampling_without_overlaps():
    """Test sampling multiple combos without card overlaps"""
    parser = RangeParser()
    combos = parser.parse_range("AA, KK, QQ, JJ, TT")
    
    sampler = WeightedRangeSampler(combos, rng=RNGManager(seed=456))
    
    # Sample multiple hands without overlaps
    samples = sampler.sample_multiple(3, allow_overlaps=False)
    
    assert len(samples) == 3, "Should sample 3 combos"
    
    # Check no card appears in multiple combos
    all_cards = []
    for combo in samples:
        all_cards.extend(combo.cards)
    
    assert len(all_cards) == len(set(all_cards)), "No card should appear in multiple combos"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])