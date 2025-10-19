"""
Strategy Simulator
Simulates different betting strategies on historical data
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from .config import (
    ENTRY_PAYOUTS, CONFIDENCE_THRESHOLDS, EV_THRESHOLDS,
    BANKROLL_STRATEGIES, DEFAULT_BACKTEST_PARAMS
)

logger = logging.getLogger(__name__)


@dataclass
class Bet:
    """Represents a single bet"""
    date: datetime
    entry_size: int
    props: List[Dict]  # List of prop predictions
    stake: float
    payout_multiplier: float
    confidence_avg: float
    expected_value: float
    sport: str
    prop_types: List[str]
    
    def __post_init__(self):
        self.potential_payout = self.stake * self.payout_multiplier
        self.outcome = None  # Will be set during evaluation
        self.actual_pnl = 0.0


@dataclass
class BettingResult:
    """Results from a betting simulation"""
    bets: List[Bet]
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    total_profit: float
    total_staked: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    longest_win_streak: int
    longest_loss_streak: int
    starting_bankroll: float
    ending_bankroll: float
    avg_bet_size: float
    daily_results: List[Dict]


class StrategySimulator:
    """
    Simulates betting strategies on historical prediction data
    """
    
    def __init__(self, historical_data: List[Dict], actual_outcomes: Dict[str, Dict]):
        """
        Initialize simulator with historical data
        
        Args:
            historical_data: List of historical predictions from database
            actual_outcomes: Dict mapping (player_id, game_id, prop_type) to actual values
        """
        self.historical_data = historical_data
        self.actual_outcomes = actual_outcomes
        self.logger = logging.getLogger(__name__)
    
    def simulate_confidence_based(
        self,
        confidence_threshold: float,
        entry_sizes: List[int],
        starting_bankroll: float,
        bet_size: float,
        bankroll_strategy: str = 'flat',
        sport: Optional[str] = None
    ) -> BettingResult:
        """
        Simulate confidence-based betting strategy
        Only bet when model confidence exceeds threshold
        """
        self.logger.info(f"Simulating confidence-based strategy (threshold={confidence_threshold}%)")
        
        # Filter predictions by confidence and sport
        filtered_predictions = self._filter_by_confidence(confidence_threshold, sport)
        
        # Generate bets
        bets = self._generate_bets(
            filtered_predictions,
            entry_sizes,
            starting_bankroll,
            bet_size,
            bankroll_strategy
        )
        
        # Evaluate bets against actual outcomes
        evaluated_bets = self._evaluate_bets(bets)
        
        # Calculate performance metrics
        return self._calculate_performance(evaluated_bets, starting_bankroll)
    
    def simulate_value_based(
        self,
        ev_threshold: float,
        entry_sizes: List[int],
        starting_bankroll: float,
        bet_size: float,
        bankroll_strategy: str = 'flat',
        sport: Optional[str] = None
    ) -> BettingResult:
        """
        Simulate value-based betting strategy
        Only bet when expected value exceeds threshold
        """
        self.logger.info(f"Simulating value-based strategy (EV threshold={ev_threshold}%)")
        
        # Filter predictions by EV and sport
        filtered_predictions = self._filter_by_ev(ev_threshold, sport)
        
        # Generate bets
        bets = self._generate_bets(
            filtered_predictions,
            entry_sizes,
            starting_bankroll,
            bet_size,
            bankroll_strategy
        )
        
        # Evaluate bets
        evaluated_bets = self._evaluate_bets(bets)
        
        # Calculate performance
        return self._calculate_performance(evaluated_bets, starting_bankroll)
    
    def simulate_prop_specific(
        self,
        prop_types: List[str],
        entry_sizes: List[int],
        starting_bankroll: float,
        bet_size: float,
        confidence_threshold: float = 0,
        bankroll_strategy: str = 'flat',
        sport: Optional[str] = None
    ) -> BettingResult:
        """
        Simulate prop-specific betting strategy
        Focus on specific prop types
        """
        self.logger.info(f"Simulating prop-specific strategy (props={prop_types})")
        
        # Filter predictions by prop types
        filtered_predictions = self._filter_by_props(prop_types, confidence_threshold, sport)
        
        # Generate bets
        bets = self._generate_bets(
            filtered_predictions,
            entry_sizes,
            starting_bankroll,
            bet_size,
            bankroll_strategy
        )
        
        # Evaluate bets
        evaluated_bets = self._evaluate_bets(bets)
        
        # Calculate performance
        return self._calculate_performance(evaluated_bets, starting_bankroll)
    
    def simulate_composite(
        self,
        confidence_threshold: float,
        ev_threshold: float,
        prop_types: Optional[List[str]],
        entry_sizes: List[int],
        starting_bankroll: float,
        bet_size: float,
        bankroll_strategy: str = 'flat',
        sport: Optional[str] = None
    ) -> BettingResult:
        """
        Simulate composite strategy with multiple filters
        """
        self.logger.info(f"Simulating composite strategy")
        
        # Apply all filters
        filtered_predictions = self.historical_data
        
        if sport:
            filtered_predictions = [p for p in filtered_predictions if p.get('sport') == sport]
        
        if confidence_threshold > 0:
            filtered_predictions = [
                p for p in filtered_predictions 
                if p.get('confidence', 0) >= confidence_threshold
            ]
        
        if ev_threshold > 0:
            filtered_predictions = [
                p for p in filtered_predictions 
                if p.get('expected_value', 0) >= ev_threshold
            ]
        
        if prop_types:
            filtered_predictions = [
                p for p in filtered_predictions 
                if p.get('prop_type') in prop_types
            ]
        
        # Generate bets
        bets = self._generate_bets(
            filtered_predictions,
            entry_sizes,
            starting_bankroll,
            bet_size,
            bankroll_strategy
        )
        
        # Evaluate bets
        evaluated_bets = self._evaluate_bets(bets)
        
        # Calculate performance
        return self._calculate_performance(evaluated_bets, starting_bankroll)
    
    def _filter_by_confidence(self, threshold: float, sport: Optional[str]) -> List[Dict]:
        """Filter predictions by confidence threshold"""
        filtered = [
            p for p in self.historical_data 
            if p.get('confidence', 0) >= threshold
        ]
        
        if sport:
            filtered = [p for p in filtered if p.get('sport') == sport]
        
        return filtered
    
    def _filter_by_ev(self, threshold: float, sport: Optional[str]) -> List[Dict]:
        """Filter predictions by expected value threshold"""
        filtered = [
            p for p in self.historical_data 
            if p.get('expected_value', 0) >= threshold
        ]
        
        if sport:
            filtered = [p for p in filtered if p.get('sport') == sport]
        
        return filtered
    
    def _filter_by_props(
        self, 
        prop_types: List[str], 
        confidence_threshold: float,
        sport: Optional[str]
    ) -> List[Dict]:
        """Filter predictions by prop types"""
        filtered = [
            p for p in self.historical_data 
            if p.get('prop_type') in prop_types 
            and p.get('confidence', 0) >= confidence_threshold
        ]
        
        if sport:
            filtered = [p for p in filtered if p.get('sport') == sport]
        
        return filtered
    
    def _generate_bets(
        self,
        predictions: List[Dict],
        entry_sizes: List[int],
        starting_bankroll: float,
        bet_size: float,
        bankroll_strategy: str
    ) -> List[Bet]:
        """
        Generate bets from predictions based on entry sizes and bankroll management
        """
        bets = []
        current_bankroll = starting_bankroll
        
        # Group predictions by date and game
        predictions_by_date = self._group_by_date(predictions)
        
        for date, date_predictions in predictions_by_date.items():
            # Try to create entries of different sizes
            for entry_size in entry_sizes:
                # Find combinations of props for this entry size
                entry_bets = self._create_entries(
                    date_predictions,
                    entry_size,
                    current_bankroll,
                    bet_size,
                    bankroll_strategy
                )
                
                bets.extend(entry_bets)
                
                # Update bankroll if using dynamic strategy
                if bankroll_strategy != 'flat':
                    for bet in entry_bets:
                        current_bankroll -= bet.stake
        
        return bets
    
    def _create_entries(
        self,
        predictions: List[Dict],
        entry_size: int,
        current_bankroll: float,
        bet_size: float,
        bankroll_strategy: str
    ) -> List[Bet]:
        """Create entry bets from available predictions"""
        entries = []
        
        # Sort by confidence/EV
        sorted_preds = sorted(
            predictions, 
            key=lambda x: (x.get('confidence', 0), x.get('expected_value', 0)), 
            reverse=True
        )
        
        # Create entries using top predictions
        i = 0
        while i + entry_size <= len(sorted_preds):
            entry_props = sorted_preds[i:i + entry_size]
            
            # Calculate bet size based on strategy
            stake = self._calculate_stake(
                current_bankroll,
                bet_size,
                bankroll_strategy,
                entry_props
            )
            
            if stake <= 0 or stake > current_bankroll:
                break
            
            # Create bet
            bet = Bet(
                date=entry_props[0]['game_date'],
                entry_size=entry_size,
                props=entry_props,
                stake=stake,
                payout_multiplier=ENTRY_PAYOUTS.get(entry_size, 1.0),
                confidence_avg=np.mean([p.get('confidence', 0) for p in entry_props]),
                expected_value=np.mean([p.get('expected_value', 0) for p in entry_props]),
                sport=entry_props[0].get('sport', 'Unknown'),
                prop_types=[p.get('prop_type') for p in entry_props]
            )
            
            entries.append(bet)
            
            # Move to next set of props (no overlap)
            i += entry_size
        
        return entries
    
    def _calculate_stake(
        self,
        current_bankroll: float,
        base_bet_size: float,
        strategy: str,
        props: List[Dict]
    ) -> float:
        """Calculate stake based on bankroll management strategy"""
        if strategy == 'flat':
            return base_bet_size
        
        elif strategy == 'percentage':
            # Bet a percentage of current bankroll
            percentage = base_bet_size  # base_bet_size is the percentage
            return current_bankroll * (percentage / 100)
        
        elif strategy == 'kelly':
            # Kelly Criterion
            # Kelly % = (edge / odds)
            avg_confidence = np.mean([p.get('confidence', 0) for p in props])
            avg_ev = np.mean([p.get('expected_value', 0) for p in props])
            
            # Simplified Kelly (assuming fair odds)
            if avg_confidence > 50 and avg_ev > 0:
                edge = avg_ev / 100  # Convert EV% to decimal
                kelly_pct = edge
                
                # Use fractional Kelly for safety (base_bet_size is the fraction)
                kelly_fraction = base_bet_size if base_bet_size <= 1 else base_bet_size / 100
                return current_bankroll * kelly_pct * kelly_fraction
            
            return 0  # No edge, no bet
        
        return base_bet_size
    
    def _group_by_date(self, predictions: List[Dict]) -> Dict[datetime, List[Dict]]:
        """Group predictions by game date"""
        grouped = {}
        
        for pred in predictions:
            date = pred.get('game_date')
            if isinstance(date, str):
                date = datetime.fromisoformat(date.split('T')[0])
            
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(pred)
        
        return dict(sorted(grouped.items()))
    
    def _evaluate_bets(self, bets: List[Bet]) -> List[Bet]:
        """Evaluate bets against actual outcomes"""
        for bet in bets:
            # Check if all props in the entry won
            all_won = True
            
            for prop in bet.props:
                key = (
                    prop.get('player_id'),
                    prop.get('game_id'),
                    prop.get('prop_type')
                )
                
                actual = self.actual_outcomes.get(key)
                
                if actual is None:
                    # Game not played yet or data missing
                    all_won = False
                    break
                
                projected = prop.get('projected_value', 0)
                actual_value = actual.get('value', 0)
                
                # Determine if this prop won (projected > actual for "under", projected < actual for "over")
                # Assuming we're betting "over" on projections
                if actual_value < projected:
                    all_won = False
                    break
            
            # Set outcome
            if all_won:
                bet.outcome = 'win'
                bet.actual_pnl = bet.potential_payout - bet.stake
            else:
                bet.outcome = 'loss'
                bet.actual_pnl = -bet.stake
        
        return bets
    
    def _calculate_performance(
        self, 
        bets: List[Bet], 
        starting_bankroll: float
    ) -> BettingResult:
        """Calculate comprehensive performance metrics"""
        if not bets:
            return self._empty_result(starting_bankroll)
        
        total_bets = len(bets)
        wins = sum(1 for b in bets if b.outcome == 'win')
        losses = total_bets - wins
        win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
        
        total_staked = sum(b.stake for b in bets)
        total_profit = sum(b.actual_pnl for b in bets)
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        
        ending_bankroll = starting_bankroll + total_profit
        avg_bet_size = total_staked / total_bets if total_bets > 0 else 0
        
        # Calculate max drawdown
        cumulative_pnl = 0
        peak = starting_bankroll
        max_drawdown = 0
        
        for bet in bets:
            cumulative_pnl += bet.actual_pnl
            current_bankroll = starting_bankroll + cumulative_pnl
            
            if current_bankroll > peak:
                peak = current_bankroll
            
            drawdown = ((peak - current_bankroll) / peak * 100) if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate Sharpe ratio
        if len(bets) > 1:
            returns = [b.actual_pnl / b.stake for b in bets]
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
        else:
            sharpe_ratio = 0
        
        # Calculate profit factor
        gross_profit = sum(b.actual_pnl for b in bets if b.actual_pnl > 0)
        gross_loss = abs(sum(b.actual_pnl for b in bets if b.actual_pnl < 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Calculate streaks
        win_streak, loss_streak = self._calculate_streaks(bets)
        
        # Calculate daily results for charting
        daily_results = self._calculate_daily_results(bets, starting_bankroll)
        
        return BettingResult(
            bets=bets,
            total_bets=total_bets,
            wins=wins,
            losses=losses,
            win_rate=round(win_rate, 2),
            total_profit=round(total_profit, 2),
            total_staked=round(total_staked, 2),
            roi=round(roi, 2),
            max_drawdown=round(max_drawdown, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            profit_factor=round(profit_factor, 2),
            longest_win_streak=win_streak,
            longest_loss_streak=loss_streak,
            starting_bankroll=starting_bankroll,
            ending_bankroll=round(ending_bankroll, 2),
            avg_bet_size=round(avg_bet_size, 2),
            daily_results=daily_results
        )
    
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio from returns"""
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return 0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return sharpe
    
    def _calculate_streaks(self, bets: List[Bet]) -> Tuple[int, int]:
        """Calculate longest win and loss streaks"""
        if not bets:
            return 0, 0
        
        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for bet in bets:
            if bet.outcome == 'win':
                current_win_streak += 1
                current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        return max_win_streak, max_loss_streak
    
    def _calculate_daily_results(self, bets: List[Bet], starting_bankroll: float) -> List[Dict]:
        """Calculate daily P&L for charting"""
        daily = {}
        cumulative_pnl = 0
        
        for bet in bets:
            date_str = bet.date.strftime('%Y-%m-%d')
            
            if date_str not in daily:
                daily[date_str] = {
                    'date': date_str,
                    'bets': 0,
                    'wins': 0,
                    'losses': 0,
                    'daily_pnl': 0,
                    'cumulative_pnl': 0,
                    'bankroll': 0
                }
            
            daily[date_str]['bets'] += 1
            daily[date_str]['wins'] += 1 if bet.outcome == 'win' else 0
            daily[date_str]['losses'] += 1 if bet.outcome == 'loss' else 0
            daily[date_str]['daily_pnl'] += bet.actual_pnl
            
            cumulative_pnl += bet.actual_pnl
            daily[date_str]['cumulative_pnl'] = round(cumulative_pnl, 2)
            daily[date_str]['bankroll'] = round(starting_bankroll + cumulative_pnl, 2)
        
        return list(daily.values())
    
    def _empty_result(self, starting_bankroll: float) -> BettingResult:
        """Return empty result when no bets"""
        return BettingResult(
            bets=[],
            total_bets=0,
            wins=0,
            losses=0,
            win_rate=0,
            total_profit=0,
            total_staked=0,
            roi=0,
            max_drawdown=0,
            sharpe_ratio=0,
            profit_factor=0,
            longest_win_streak=0,
            longest_loss_streak=0,
            starting_bankroll=starting_bankroll,
            ending_bankroll=starting_bankroll,
            avg_bet_size=0,
            daily_results=[]
        )
