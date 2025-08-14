#!/usr/bin/env python3
"""
Unit tests for the Range Parser module
Range 解析器模块的单元测试

Tests all major functionality of the poker range parser including:
- Basic hand parsing (AA, AKs, AKo, AK)
- Plus ranges (QQ+, AKs+)
- Dash ranges (QQ-88, AKs-ATs)
- Complex multi-part ranges
- Range vs range equity calculations
"""

import unittest
from range_parser import HandRange, parse_ranges, calculate_range_vs_range_equity
from texas_holdem_calculator import Card, Rank, Suit, parse_card_string

class TestHandRange(unittest.TestCase):
    """Test cases for HandRange class"""
    
    def test_pocket_pairs(self):
        """Test pocket pair parsing"""
        # Single pocket pair
        range_obj = parse_ranges("AA")
        self.assertEqual(range_obj.size(), 6)  # 6 combinations of AA
        
        range_obj = parse_ranges("KK")
        self.assertEqual(range_obj.size(), 6)
        
        # Plus ranges
        range_obj = parse_ranges("QQ+")
        self.assertEqual(range_obj.size(), 18)  # QQ, KK, AA = 6+6+6
        
        range_obj = parse_ranges("88+")
        self.assertEqual(range_obj.size(), 42)  # 88 through AA = 7 pairs * 6
        
        # Dash ranges
        range_obj = parse_ranges("QQ-JJ")
        self.assertEqual(range_obj.size(), 12)  # QQ and JJ = 6+6
        
        range_obj = parse_ranges("77-22")
        self.assertEqual(range_obj.size(), 36)  # 6 pairs * 6 combinations each
    
    def test_suited_hands(self):
        """Test suited hand parsing"""
        # Single suited hand
        range_obj = parse_ranges("AKs")
        self.assertEqual(range_obj.size(), 4)  # 4 suits
        
        range_obj = parse_ranges("KQs")
        self.assertEqual(range_obj.size(), 4)
        
        # Suited ranges
        range_obj = parse_ranges("AKs-ATs")
        self.assertEqual(range_obj.size(), 16)  # AK, AQ, AJ, AT = 4 hands * 4 suits
        
        range_obj = parse_ranges("KQs-K9s")
        self.assertEqual(range_obj.size(), 16)  # KQ, KJ, KT, K9 = 4 hands * 4 suits
    
    def test_offsuit_hands(self):
        """Test offsuit hand parsing"""
        # Single offsuit hand  
        range_obj = parse_ranges("AKo")
        self.assertEqual(range_obj.size(), 12)  # 4*3 = 12 combinations
        
        range_obj = parse_ranges("KQo")
        self.assertEqual(range_obj.size(), 12)
        
        # Plus ranges
        range_obj = parse_ranges("T9o+")
        self.assertEqual(range_obj.size(), 12)  # Only T9o (kicker can't be higher than T)
    
    def test_any_hands(self):
        """Test 'any' hands (both suited and offsuit)"""
        # AK should include both AKs and AKo
        range_obj = parse_ranges("AK")
        self.assertEqual(range_obj.size(), 16)  # 4 suited + 12 offsuit
        
        range_obj = parse_ranges("KQ")
        self.assertEqual(range_obj.size(), 16)
    
    def test_complex_ranges(self):
        """Test complex multi-part ranges"""
        # Multiple parts
        range_obj = parse_ranges("AA, KK, QQ")
        self.assertEqual(range_obj.size(), 18)  # 3 pairs * 6 combinations
        
        range_obj = parse_ranges("AA-QQ, AKs, KQo")
        expected_size = 18 + 4 + 12  # (AA,KK,QQ) + AKs + KQo
        self.assertEqual(range_obj.size(), expected_size)
        
        # Complex mixed range
        range_obj = parse_ranges("88+, AKs-AJs, KQo+")
        # 88+ = 7 pairs * 6 = 42
        # AKs-AJs = 3 hands * 4 = 12  
        # KQo+ = 1 hand * 12 = 12
        expected_size = 42 + 12 + 12
        self.assertEqual(range_obj.size(), expected_size)
    
    def test_case_insensitivity(self):
        """Test that parser handles different cases correctly"""
        range1 = parse_ranges("AKs")
        range2 = parse_ranges("aks")
        range3 = parse_ranges("Aks")
        
        self.assertEqual(range1.size(), range2.size())
        self.assertEqual(range1.size(), range3.size())
        self.assertEqual(range1.size(), 4)
    
    def test_whitespace_handling(self):
        """Test that parser handles whitespace correctly"""
        range1 = parse_ranges("AA,KK,QQ")
        range2 = parse_ranges("AA, KK, QQ")
        range3 = parse_ranges(" AA , KK , QQ ")
        
        self.assertEqual(range1.size(), range2.size())
        self.assertEqual(range1.size(), range3.size())
        self.assertEqual(range1.size(), 18)
    
    def test_error_handling(self):
        """Test error handling for invalid ranges"""
        # Invalid single hands should result in 0 combinations
        range_obj = parse_ranges("ZZ")  # Invalid rank
        self.assertEqual(range_obj.size(), 0)
        
        range_obj = parse_ranges("A1s")  # Invalid rank
        self.assertEqual(range_obj.size(), 0)
        
        # Empty range
        range_obj = parse_ranges("")
        self.assertEqual(range_obj.size(), 0)
        
        # Just commas
        range_obj = parse_ranges(", , ,")
        self.assertEqual(range_obj.size(), 0)
    
    def test_board_card_filtering(self):
        """Test filtering out combinations that conflict with board cards"""
        # Create a range and filter with board cards
        range_obj = parse_ranges("AA")
        board_cards = [parse_card_string("As")]  # One ace on board
        
        filtered_range = range_obj.remove_conflicting(board_cards)
        # Should have fewer combinations now
        self.assertLess(filtered_range.size(), range_obj.size())
        
        # Test with multiple board cards
        board_cards = [parse_card_string("As"), parse_card_string("Ah")]
        filtered_range = range_obj.remove_conflicting(board_cards)
        # Should have even fewer combinations
        self.assertEqual(filtered_range.size(), 1)  # Only AdAc remains
    
    def test_range_intersections(self):
        """Test checking for range intersections with other cards"""
        range_obj = parse_ranges("AA")
        
        # Should intersect with Ace
        cards = [parse_card_string("As")]
        self.assertTrue(range_obj.intersects_with(cards))
        
        # Should not intersect with King
        cards = [parse_card_string("Ks")]
        self.assertFalse(range_obj.intersects_with(cards))
    
    def test_specific_combinations(self):
        """Test that specific combinations are generated correctly"""
        # Test AA generates correct combinations
        range_obj = parse_ranges("AA")
        combinations = range_obj.get_combinations()
        
        # Should have 6 combinations
        self.assertEqual(len(combinations), 6)
        
        # All should be aces
        for c1, c2 in combinations:
            self.assertEqual(c1.rank, Rank.ACE)
            self.assertEqual(c2.rank, Rank.ACE)
            self.assertNotEqual(c1.suit, c2.suit)  # Different suits
        
        # Test AKs generates correct combinations
        range_obj = parse_ranges("AKs")
        combinations = range_obj.get_combinations()
        
        self.assertEqual(len(combinations), 4)
        for c1, c2 in combinations:
            # Should be ace and king
            ranks = {c1.rank, c2.rank}
            self.assertEqual(ranks, {Rank.ACE, Rank.KING})
            # Should be same suit
            self.assertEqual(c1.suit, c2.suit)

class TestRangeVsRangeEquity(unittest.TestCase):
    """Test cases for range vs range equity calculations"""
    
    def test_basic_range_vs_range(self):
        """Test basic range vs range equity calculation"""
        result = calculate_range_vs_range_equity(
            hero_range="AA",
            villain_range="KK", 
            num_simulations=1000
        )
        
        # AA should beat KK most of the time
        self.assertGreater(result['hero_equity'], 0.75)
        self.assertLess(result['villain_equity'], 0.25)
        self.assertEqual(result['hero_combos'], 6)
        self.assertEqual(result['villain_combos'], 6)
    
    def test_range_vs_range_with_board(self):
        """Test range vs range with board cards"""
        board_cards = [parse_card_string("As"), parse_card_string("2h"), parse_card_string("3c")]
        
        result = calculate_range_vs_range_equity(
            hero_range="AA",  # Will be filtered to remove As combinations
            villain_range="KK",
            community_cards=board_cards,
            num_simulations=1000
        )
        
        # Should still work but with fewer hero combinations
        self.assertGreater(result['hero_equity'], 0.75)
        self.assertLess(result['hero_combos'], 6)  # Some AA combos filtered out
        self.assertEqual(result['villain_combos'], 6)  # KK unaffected
    
    def test_empty_range_handling(self):
        """Test handling of empty ranges after filtering"""
        # Board has all aces
        board_cards = [
            parse_card_string("As"), parse_card_string("Ah"),
            parse_card_string("Ad"), parse_card_string("Ac")
        ]
        
        result = calculate_range_vs_range_equity(
            hero_range="AA",  # All combos will be filtered out
            villain_range="KK",
            community_cards=board_cards,
            num_simulations=1000
        )
        
        # Should return error
        self.assertIn('error', result)

class TestRangeParsingEdgeCases(unittest.TestCase):
    """Test edge cases and corner cases in range parsing"""
    
    def test_wheel_and_broadway(self):
        """Test parsing of wheel and broadway ranges"""
        # Wheel suited connectors
        range_obj = parse_ranges("A5s-A2s")
        self.assertEqual(range_obj.size(), 16)  # A5s, A4s, A3s, A2s = 4*4
        
        # Broadway
        range_obj = parse_ranges("AKs-ATs")
        self.assertEqual(range_obj.size(), 16)  # AKs, AQs, AJs, ATs = 4*4
    
    def test_single_rank_ranges(self):
        """Test ranges with single ranks"""
        # KK-KK should just be KK
        range_obj = parse_ranges("KK-KK")
        self.assertEqual(range_obj.size(), 6)
        
        # AKs-AKs should just be AKs
        range_obj = parse_ranges("AKs-AKs")
        self.assertEqual(range_obj.size(), 4)
    
    def test_deduplication(self):
        """Test that duplicate combinations are removed"""
        # AA,AA should be the same as AA
        range1 = parse_ranges("AA")
        range2 = parse_ranges("AA,AA")
        
        self.assertEqual(range1.size(), range2.size())
        
        # AK,AKs,AKo should be the same as AK (since AK includes both)
        range1 = parse_ranges("AK")
        range2 = parse_ranges("AK,AKs,AKo")
        
        self.assertEqual(range1.size(), range2.size())

def run_range_parser_tests():
    """Run all range parser tests"""
    print("🧪 Running Range Parser Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestHandRange,
        TestRangeVsRangeEquity, 
        TestRangeParsingEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 RANGE PARSER TEST SUMMARY")
    print("-" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All range parser tests passed!")
        return True
    else:
        print("\n❌ Some tests failed.")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  {test}: {traceback}")
        
        return False

if __name__ == "__main__":
    success = run_range_parser_tests()
    exit(0 if success else 1)