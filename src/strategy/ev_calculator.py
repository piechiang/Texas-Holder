"""
Expected Value (EV) Calculator with Break-even Analysis
期望值计算器和盈亏平衡分析
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

# Add parent directory to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from texas_holdem_calculator import Card, BettingContext, BettingDecision
from src.core.equity_result import EquityResult
from src.core.dispatcher import compute_equity
from src.strategy.ranges import WeightedRangeSampler, Combo, parse_ranges


class ActionType(Enum):
    """Possible poker actions"""
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass
class EVScenario:
    """
    EV calculation scenario with betting context
    包含下注上下文的EV计算场景
    """
    hero_range: Union[List[Card], WeightedRangeSampler, str]
    villain_ranges: List[Union[List[Card], WeightedRangeSampler, str]]
    community_cards: List[Card]
    pot_size: float
    bet_to_call: float
    stack_size: float
    position: str = "BTN"
    betting_round: str = "preflop"
    
    @property
    def pot_odds(self) -> float:
        """Calculate pot odds required to call"""
        if self.pot_size + self.bet_to_call <= 0:
            return 0.0
        return self.bet_to_call / (self.pot_size + self.bet_to_call)
    
    @property 
    def total_pot_after_call(self) -> float:
        """Total pot size after calling"""
        return self.pot_size + self.bet_to_call


@dataclass
class BreakevenAnalysis:
    """
    Advanced break-even analysis with multiple betting scenarios
    高级盈亏平衡分析，支持多种下注场景
    """
    pot_odds: float
    required_equity: float
    current_equity: float
    equity_surplus: float
    
    # Multi-street analysis
    implied_odds: float = 0.0
    reverse_implied_odds: float = 0.0
    future_pot_potential: float = 0.0
    
    # Risk analysis
    risk_reward_ratio: float = 0.0
    kelly_criterion: float = 0.0
    
    # Decision thresholds
    conservative_threshold: float = 0.02  # Need 2% equity surplus for conservative play
    aggressive_threshold: float = -0.01   # Can accept 1% deficit for aggressive play
    
    def __post_init__(self):
        """Calculate derived metrics"""
        if self.pot_odds > 0:
            self.risk_reward_ratio = (1 - self.pot_odds) / self.pot_odds
        
        # Kelly Criterion: f = (bp - q) / b where b = odds, p = win prob, q = lose prob
        if self.pot_odds > 0 and self.pot_odds < 1:
            odds = (1 - self.pot_odds) / self.pot_odds
            self.kelly_criterion = (odds * self.current_equity - (1 - self.current_equity)) / odds
    
    @property
    def is_profitable(self) -> bool:
        """Check if call is profitable"""
        return self.equity_surplus > 0
    
    @property
    def is_breakeven(self) -> bool:
        """Check if call is near break-even"""
        return abs(self.equity_surplus) < 0.001
    
    @property
    def decision_confidence(self) -> str:
        """Get confidence level for decision"""
        if self.equity_surplus >= self.conservative_threshold:
            return "High (Conservative Play)"
        elif self.equity_surplus > 0:
            return "Medium (Slight Edge)" 
        elif self.equity_surplus >= self.aggressive_threshold:
            return "Low (Marginal Spot)"
        else:
            return "Very Low (Clear Fold)"
    
    @property
    def recommendation_reason(self) -> str:
        """Get detailed reasoning for recommendation"""
        equity_pct = self.current_equity * 100
        required_pct = self.required_equity * 100
        surplus_pct = self.equity_surplus * 100
        
        if self.is_profitable:
            return (
                f"Call profitable: Need {required_pct:.1f}% equity, have {equity_pct:.1f}% "
                f"(+{surplus_pct:.1f}% surplus)"
            )
        else:
            return (
                f"Call unprofitable: Need {required_pct:.1f}% equity, have {equity_pct:.1f}% "
                f"({surplus_pct:.1f}% deficit)"
            )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "pot_odds": self.pot_odds,
            "required_equity": self.required_equity,
            "current_equity": self.current_equity,
            "equity_surplus": self.equity_surplus,
            "implied_odds": self.implied_odds,
            "reverse_implied_odds": self.reverse_implied_odds,
            "future_pot_potential": self.future_pot_potential,
            "risk_reward_ratio": self.risk_reward_ratio,
            "kelly_criterion": self.kelly_criterion,
            "is_profitable": self.is_profitable,
            "is_breakeven": self.is_breakeven,
            "decision_confidence": self.decision_confidence,
            "recommendation_reason": self.recommendation_reason
        }


@dataclass
class EVResult:
    """
    Expected Value calculation result with detailed analysis
    期望值计算结果和详细分析
    """
    scenario: EVScenario
    equity_result: EquityResult
    
    # EV calculations for different actions
    ev_fold: float = 0.0  # Always 0
    ev_call: float = 0.0
    ev_raise: Optional[float] = None
    ev_all_in: Optional[float] = None
    
    # Enhanced break-even analysis
    breakeven_analysis: Optional[BreakevenAnalysis] = None
    
    # Recommendations
    recommended_action: ActionType = ActionType.FOLD
    confidence_level: str = "Low"
    reasoning: str = ""
    
    # Additional analysis
    pot_odds: float = 0.0
    implied_odds_factor: float = 1.0
    reverse_implied_odds_factor: float = 1.0
    
    def __post_init__(self):
        """Calculate derived values after initialization"""
        self.pot_odds = self.scenario.pot_odds
        
        # Create comprehensive break-even analysis
        if self.breakeven_analysis is None:
            self.breakeven_analysis = calculate_breakeven_analysis(
                pot_size=self.scenario.pot_size,
                bet_to_call=self.scenario.bet_to_call,
                current_equity=self.equity_result.p_hat
            )
    
    @property
    def breakeven_equity(self) -> float:
        """Backward compatibility property"""
        return self.breakeven_analysis.required_equity if self.breakeven_analysis else self.pot_odds
    
    @property 
    def equity_surplus(self) -> float:
        """Backward compatibility property"""
        return self.breakeven_analysis.equity_surplus if self.breakeven_analysis else 0.0
    
    @property
    def best_ev(self) -> float:
        """Get the highest EV among all actions"""
        evs = [self.ev_fold, self.ev_call]
        if self.ev_raise is not None:
            evs.append(self.ev_raise)
        if self.ev_all_in is not None:
            evs.append(self.ev_all_in)
        return max(evs)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            "equity": {
                "win_probability": self.equity_result.p_hat,
                "ci_low": self.equity_result.ci_low,
                "ci_high": self.equity_result.ci_high,
                "samples": self.equity_result.n,
                "method": self.equity_result.mode
            },
            "ev_analysis": {
                "ev_fold": self.ev_fold,
                "ev_call": self.ev_call,
                "ev_raise": self.ev_raise,
                "ev_all_in": self.ev_all_in,
                "best_ev": self.best_ev
            },
            "recommendation": {
                "action": self.recommended_action.value,
                "confidence": self.confidence_level,
                "reasoning": self.reasoning
            },
            "scenario": {
                "pot_size": self.scenario.pot_size,
                "bet_to_call": self.scenario.bet_to_call,
                "stack_size": self.scenario.stack_size,
                "position": self.scenario.position,
                "betting_round": self.scenario.betting_round
            }
        }
        
        # Add enhanced break-even analysis if available
        if self.breakeven_analysis:
            result["breakeven_analysis"] = self.breakeven_analysis.to_dict()
        else:
            # Fallback to basic analysis
            result["breakeven_analysis"] = {
                "required_equity": self.breakeven_equity,
                "actual_equity": self.equity_result.p_hat,
                "equity_surplus": self.equity_surplus,
                "pot_odds": self.pot_odds
            }
        
        return result


class EVCalculator:
    """
    Expected Value calculator for poker scenarios with range support
    支持范围的扑克场景期望值计算器
    """
    
    def __init__(self, use_fast_evaluator: bool = True):
        """Initialize EV calculator"""
        self.use_fast_evaluator = use_fast_evaluator
    
    def calculate_ev(
        self, 
        scenario: EVScenario,
        raise_size: Optional[float] = None,
        fold_equity: float = 0.0,  # Probability villain folds to raise
        implied_odds_multiplier: float = 1.0,  # Future betting rounds multiplier
        target_ci: float = 0.01,
        max_iter: int = 100_000,
        seed: Optional[int] = None,
        verbose: bool = False
    ) -> EVResult:
        """
        Calculate EV for all possible actions in a scenario
        计算场景中所有可能行动的期望值
        
        Args:
            scenario: The poker scenario to analyze
            raise_size: Optional raise amount for raise EV calculation
            fold_equity: Probability that villain folds to a raise
            implied_odds_multiplier: Multiplier for future betting value
            target_ci: Target confidence interval for equity calculation
            max_iter: Maximum iterations for Monte Carlo
            seed: Random seed for reproducibility
            verbose: Print detailed analysis
            
        Returns:
            EVResult with complete analysis
        """
        # Step 1: Calculate equity using existing infrastructure
        equity_result = self._calculate_equity(
            scenario, target_ci, max_iter, seed, verbose
        )
        
        # Step 2: Calculate EV for each action
        ev_fold = 0.0  # Folding always gives 0 EV
        
        ev_call = self._calculate_call_ev(
            scenario, equity_result, implied_odds_multiplier
        )
        
        ev_raise = None
        ev_all_in = None
        
        if raise_size is not None and raise_size > 0:
            ev_raise = self._calculate_raise_ev(
                scenario, equity_result, raise_size, fold_equity, implied_odds_multiplier
            )
        
        # All-in EV (if stack allows)
        if scenario.stack_size > scenario.bet_to_call:
            all_in_size = scenario.stack_size
            ev_all_in = self._calculate_raise_ev(
                scenario, equity_result, all_in_size, fold_equity * 1.5, implied_odds_multiplier
            )
        
        # Step 3: Create result with analysis
        result = EVResult(
            scenario=scenario,
            equity_result=equity_result,
            ev_fold=ev_fold,
            ev_call=ev_call,
            ev_raise=ev_raise,
            ev_all_in=ev_all_in
        )
        
        # Step 4: Determine recommendation
        self._analyze_recommendation(result, verbose)
        
        return result
    
    def _calculate_equity(
        self, 
        scenario: EVScenario, 
        target_ci: float, 
        max_iter: int, 
        seed: Optional[int],
        verbose: bool
    ) -> EquityResult:
        """Calculate equity using range-aware computation"""
        
        # Handle different input types for hero
        if isinstance(scenario.hero_range, list):
            # Specific hero cards
            hero_cards = scenario.hero_range
        elif isinstance(scenario.hero_range, str):
            if scenario.hero_range.lower() == "random":
                # For random, we'll need a different approach
                # For now, use a default strong range
                hero_sampler = parse_ranges("JJ+, AKs, AQs")
                hero_combo = hero_sampler.sample(scenario.community_cards)
                hero_cards = list(hero_combo.cards) if hero_combo else []
            else:
                # Parse as range and sample
                hero_sampler = parse_ranges(scenario.hero_range)
                hero_combo = hero_sampler.sample(scenario.community_cards)
                hero_cards = list(hero_combo.cards) if hero_combo else []
        elif isinstance(scenario.hero_range, WeightedRangeSampler):
            # Sample from range
            hero_combo = scenario.hero_range.sample(scenario.community_cards)
            hero_cards = list(hero_combo.cards) if hero_combo else []
        else:
            raise ValueError(f"Invalid hero range type: {type(scenario.hero_range)}")
        
        if not hero_cards:
            raise ValueError("Could not determine hero cards from range")
        
        # Handle villain ranges - for now, convert to "random" for simplicity
        # In a full implementation, this would use range-vs-range calculation
        villain_specs = []
        for villain_range in scenario.villain_ranges:
            if isinstance(villain_range, list):
                villain_specs.append(villain_range)
            else:
                villain_specs.append("random")  # Simplification for now
        
        # Calculate equity using existing dispatcher
        return compute_equity(
            hero_cards=hero_cards,
            opponent_specs=villain_specs,
            community_cards=scenario.community_cards,
            target_ci=target_ci,
            max_iter=max_iter,
            seed=seed,
            verbose=verbose
        )
    
    def _calculate_call_ev(
        self, 
        scenario: EVScenario, 
        equity_result: EquityResult,
        implied_odds_multiplier: float
    ) -> float:
        """
        Calculate EV of calling
        计算跟注的期望值
        
        EV(call) = P(win) * (pot_after_call) - bet_to_call
        """
        win_probability = equity_result.p_hat
        tie_probability = equity_result.tie_probability
        
        # Pot after call includes our call and the current pot
        pot_after_call = scenario.total_pot_after_call
        
        # Basic call EV: win full pot when winning, get half when tying
        ev_call = (
            win_probability * pot_after_call + 
            tie_probability * (pot_after_call / 2) - 
            scenario.bet_to_call
        )
        
        # Adjust for implied odds (future betting rounds)
        if implied_odds_multiplier > 1.0:
            implied_value = (win_probability * scenario.bet_to_call * 
                           (implied_odds_multiplier - 1.0))
            ev_call += implied_value
        
        return ev_call
    
    def _calculate_raise_ev(
        self, 
        scenario: EVScenario, 
        equity_result: EquityResult,
        raise_size: float,
        fold_equity: float,
        implied_odds_multiplier: float
    ) -> float:
        """
        Calculate EV of raising
        计算加注的期望值
        
        EV(raise) = P(fold) * current_pot + P(call) * EV_if_called
        """
        win_probability = equity_result.p_hat
        tie_probability = equity_result.tie_probability
        
        # Immediate win from fold
        fold_ev = fold_equity * scenario.pot_size
        
        # EV when called (simplified)
        call_probability = 1.0 - fold_equity
        pot_after_raise = scenario.pot_size + 2 * raise_size  # Our raise + villain call
        
        ev_if_called = (
            win_probability * pot_after_raise +
            tie_probability * (pot_after_raise / 2) -
            raise_size
        )
        
        # Adjust for implied odds
        if implied_odds_multiplier > 1.0:
            implied_value = (win_probability * raise_size * 
                           (implied_odds_multiplier - 1.0))
            ev_if_called += implied_value
        
        total_ev = fold_ev + call_probability * ev_if_called
        
        return total_ev
    
    def _analyze_recommendation(self, result: EVResult, verbose: bool = False):
        """
        Enhanced recommendation analysis using break-even analysis
        使用盈亏平衡分析的增强决策建议
        """
        # Find best action based on EV
        actions_evs = [
            (ActionType.FOLD, result.ev_fold),
            (ActionType.CALL, result.ev_call)
        ]
        
        if result.ev_raise is not None:
            actions_evs.append((ActionType.RAISE, result.ev_raise))
        
        if result.ev_all_in is not None:
            actions_evs.append((ActionType.ALL_IN, result.ev_all_in))
        
        # Sort by EV
        actions_evs.sort(key=lambda x: x[1], reverse=True)
        best_action, best_ev = actions_evs[0]
        
        result.recommended_action = best_action
        
        # Use break-even analysis for confidence and reasoning
        if result.breakeven_analysis:
            # Use enhanced confidence from break-even analysis
            result.confidence_level = result.breakeven_analysis.decision_confidence
            
            # Enhanced reasoning incorporating multiple factors
            equity_pct = result.equity_result.p_hat * 100
            pot_odds_pct = result.pot_odds * 100
            kelly = result.breakeven_analysis.kelly_criterion
            
            if best_action == ActionType.FOLD:
                result.reasoning = (
                    f"Fold recommended: {result.breakeven_analysis.recommendation_reason}. "
                    f"Kelly criterion: {kelly:.3f} (negative suggests folding)"
                )
            elif best_action == ActionType.CALL:
                if result.breakeven_analysis.is_profitable:
                    result.reasoning = (
                        f"Call recommended: {result.breakeven_analysis.recommendation_reason}. "
                        f"Kelly criterion: {kelly:.3f} suggests betting {kelly*100:.1f}% of bankroll"
                    )
                else:
                    result.reasoning = (
                        f"Marginal call: {result.breakeven_analysis.recommendation_reason}. "
                        f"Consider implied odds and position"
                    )
            elif best_action == ActionType.RAISE:
                result.reasoning = (
                    f"Raise recommended: EV(raise) ${best_ev:.2f} > EV(call) ${result.ev_call:.2f}. "
                    f"Strong equity advantage ({equity_pct:.1f}% vs {pot_odds_pct:.1f}% required)"
                )
            elif best_action == ActionType.ALL_IN:
                result.reasoning = (
                    f"All-in recommended: EV(all-in) ${best_ev:.2f} maximizes value. "
                    f"Dominant equity position ({equity_pct:.1f}%)"
                )
        else:
            # Fallback to basic analysis
            equity_surplus = result.equity_surplus
            
            if abs(equity_surplus) < 0.02:
                confidence = "Low"
            elif abs(equity_surplus) < 0.05:
                confidence = "Medium"
            else:
                confidence = "High"
            
            result.confidence_level = confidence
            
            equity_pct = result.equity_result.p_hat * 100
            pot_odds_pct = result.pot_odds * 100
            
            if best_action == ActionType.FOLD:
                result.reasoning = (
                    f"Fold recommended: Equity {equity_pct:.1f}% < "
                    f"Required {pot_odds_pct:.1f}% (deficit: {-equity_surplus*100:.1f}%)"
                )
            elif best_action == ActionType.CALL:
                result.reasoning = (
                    f"Call recommended: Equity {equity_pct:.1f}% > "
                    f"Required {pot_odds_pct:.1f}% (surplus: {equity_surplus*100:.1f}%)"
                )
        
        if verbose:
            print(f"Recommendation: {best_action.value.upper()}")
            print(f"Confidence: {result.confidence_level}")
            print(f"Reasoning: {result.reasoning}")
            
            if result.breakeven_analysis:
                print(f"Break-even Analysis:")
                print(f"  Pot Odds: {result.breakeven_analysis.pot_odds:.1%}")
                print(f"  Risk/Reward: {result.breakeven_analysis.risk_reward_ratio:.2f}:1")
                print(f"  Kelly Criterion: {result.breakeven_analysis.kelly_criterion:.3f}")
                print(f"  Implied Odds: {result.breakeven_analysis.implied_odds:.1%}")
                if result.breakeven_analysis.future_pot_potential > 0:
                    print(f"  Future Pot Potential: ${result.breakeven_analysis.future_pot_potential:.0f}")


def calculate_breakeven_analysis(
    pot_size: float, 
    bet_to_call: float,
    current_equity: float,
    future_betting_rounds: int = 1,
    average_future_bet_ratio: float = 0.7,
    opponent_stack_ratio: float = 1.0
) -> BreakevenAnalysis:
    """
    Calculate comprehensive break-even analysis for a betting situation
    计算下注情况的综合盈亏平衡分析
    
    Args:
        pot_size: Current pot size
        bet_to_call: Amount needed to call
        current_equity: Current win probability
        future_betting_rounds: Expected number of future betting rounds
        average_future_bet_ratio: Expected ratio of future bets to current pot
        opponent_stack_ratio: Ratio of opponent stack to current pot
        
    Returns:
        BreakevenAnalysis object with comprehensive metrics
    """
    pot_odds = bet_to_call / (pot_size + bet_to_call) if (pot_size + bet_to_call) > 0 else 0
    equity_surplus = current_equity - pot_odds
    
    # Calculate implied odds (simplified)
    future_pot_potential = pot_size * future_betting_rounds * average_future_bet_ratio
    implied_odds_factor = min(1.0 + future_pot_potential / pot_size * 0.2, 2.0)  # Cap at 2x
    implied_odds = pot_odds / implied_odds_factor if implied_odds_factor > 0 else pot_odds
    
    # Calculate reverse implied odds (when we're behind and improve to second-best)
    reverse_implied_multiplier = max(0.8, 1.0 - opponent_stack_ratio * 0.1)
    reverse_implied_odds = pot_odds * reverse_implied_multiplier
    
    return BreakevenAnalysis(
        pot_odds=pot_odds,
        required_equity=pot_odds,
        current_equity=current_equity,
        equity_surplus=equity_surplus,
        implied_odds=implied_odds,
        reverse_implied_odds=reverse_implied_odds,
        future_pot_potential=future_pot_potential
    )


# Convenience functions for common calculations
def quick_ev_analysis(
    hero_range: str,
    villain_range: str, 
    community_cards: List[Card],
    pot_size: float,
    bet_to_call: float,
    stack_size: float,
    verbose: bool = True
) -> EVResult:
    """
    Quick EV analysis for common scenarios
    常见场景的快速EV分析
    """
    scenario = EVScenario(
        hero_range=hero_range,
        villain_ranges=[villain_range],
        community_cards=community_cards,
        pot_size=pot_size,
        bet_to_call=bet_to_call,
        stack_size=stack_size
    )
    
    calculator = EVCalculator()
    return calculator.calculate_ev(scenario, verbose=verbose)