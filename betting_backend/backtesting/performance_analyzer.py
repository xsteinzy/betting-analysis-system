"""
Performance Analyzer
Analyzes betting performance across different dimensions
"""

import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import numpy as np
from .strategy_simulator import BettingResult, Bet
from .config import ENTRY_PAYOUTS, PROP_TYPES

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    Analyzes betting performance across various dimensions:
    - Entry size (2-pick, 3-pick, etc.)
    - Prop type (Points, Assists, etc.)
    - Sport (NBA vs NFL)
    - Confidence levels
    - Time periods
    """
    
    def __init__(self, betting_result: BettingResult):
        """Initialize analyzer with betting results"""
        self.result = betting_result
        self.bets = betting_result.bets
        self.logger = logging.getLogger(__name__)
    
    def analyze_by_entry_size(self) -> Dict[int, Dict]:
        """
        Analyze performance by entry size (2-pick, 3-pick, 4-pick, 5-pick)
        """
        self.logger.info("Analyzing performance by entry size")
        
        entry_performance = defaultdict(lambda: {
            'bets': [],
            'count': 0,
            'wins': 0,
            'losses': 0,
            'total_staked': 0,
            'total_profit': 0
        })
        
        for bet in self.bets:
            size = bet.entry_size
            entry_performance[size]['bets'].append(bet)
            entry_performance[size]['count'] += 1
            entry_performance[size]['wins'] += 1 if bet.outcome == 'win' else 0
            entry_performance[size]['losses'] += 1 if bet.outcome == 'loss' else 0
            entry_performance[size]['total_staked'] += bet.stake
            entry_performance[size]['total_profit'] += bet.actual_pnl
        
        # Calculate metrics for each entry size
        results = {}
        for size, data in entry_performance.items():
            if data['count'] > 0:
                win_rate = (data['wins'] / data['count']) * 100
                roi = (data['total_profit'] / data['total_staked']) * 100 if data['total_staked'] > 0 else 0
                avg_profit = data['total_profit'] / data['count']
                
                results[size] = {
                    'entry_size': size,
                    'total_bets': data['count'],
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'win_rate': round(win_rate, 2),
                    'total_staked': round(data['total_staked'], 2),
                    'total_profit': round(data['total_profit'], 2),
                    'roi': round(roi, 2),
                    'avg_profit_per_bet': round(avg_profit, 2),
                    'payout_multiplier': ENTRY_PAYOUTS.get(size, 1.0)
                }
        
        return dict(sorted(results.items()))
    
    def analyze_by_prop_type(self) -> Dict[str, Dict]:
        """
        Analyze performance by prop type
        """
        self.logger.info("Analyzing performance by prop type")
        
        prop_performance = defaultdict(lambda: {
            'appearances': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0,
            'total_profit': 0,
            'avg_confidence': []
        })
        
        for bet in self.bets:
            for prop_type in bet.prop_types:
                prop_performance[prop_type]['appearances'] += 1
                prop_performance[prop_type]['wins'] += 1 if bet.outcome == 'win' else 0
                prop_performance[prop_type]['losses'] += 1 if bet.outcome == 'loss' else 0
                prop_performance[prop_type]['total_profit'] += bet.actual_pnl
                
                # Get confidence for this specific prop
                for prop in bet.props:
                    if prop.get('prop_type') == prop_type:
                        prop_performance[prop_type]['avg_confidence'].append(
                            prop.get('confidence', 0)
                        )
        
        # Calculate metrics
        results = {}
        for prop_type, data in prop_performance.items():
            if data['appearances'] > 0:
                win_rate = (data['wins'] / data['appearances']) * 100
                avg_conf = np.mean(data['avg_confidence']) if data['avg_confidence'] else 0
                
                results[prop_type] = {
                    'prop_type': prop_type,
                    'appearances': data['appearances'],
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'win_rate': round(win_rate, 2),
                    'total_profit': round(data['total_profit'], 2),
                    'avg_confidence': round(avg_conf, 2)
                }
        
        # Sort by win rate
        return dict(sorted(results.items(), key=lambda x: x[1]['win_rate'], reverse=True))
    
    def analyze_by_sport(self) -> Dict[str, Dict]:
        """
        Analyze performance by sport (NBA vs NFL)
        """
        self.logger.info("Analyzing performance by sport")
        
        sport_performance = defaultdict(lambda: {
            'bets': 0,
            'wins': 0,
            'losses': 0,
            'total_staked': 0,
            'total_profit': 0
        })
        
        for bet in self.bets:
            sport = bet.sport
            sport_performance[sport]['bets'] += 1
            sport_performance[sport]['wins'] += 1 if bet.outcome == 'win' else 0
            sport_performance[sport]['losses'] += 1 if bet.outcome == 'loss' else 0
            sport_performance[sport]['total_staked'] += bet.stake
            sport_performance[sport]['total_profit'] += bet.actual_pnl
        
        # Calculate metrics
        results = {}
        for sport, data in sport_performance.items():
            if data['bets'] > 0:
                win_rate = (data['wins'] / data['bets']) * 100
                roi = (data['total_profit'] / data['total_staked']) * 100 if data['total_staked'] > 0 else 0
                
                results[sport] = {
                    'sport': sport,
                    'total_bets': data['bets'],
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'win_rate': round(win_rate, 2),
                    'total_staked': round(data['total_staked'], 2),
                    'total_profit': round(data['total_profit'], 2),
                    'roi': round(roi, 2)
                }
        
        return results
    
    def analyze_by_confidence_level(self, buckets: List[Tuple[int, int]] = None) -> Dict[str, Dict]:
        """
        Analyze performance by confidence level buckets
        Default buckets: 60-70, 70-80, 80-90, 90-100
        """
        if buckets is None:
            buckets = [(60, 70), (70, 80), (80, 90), (90, 100)]
        
        self.logger.info("Analyzing performance by confidence level")
        
        confidence_performance = defaultdict(lambda: {
            'bets': 0,
            'wins': 0,
            'losses': 0,
            'total_staked': 0,
            'total_profit': 0
        })
        
        for bet in self.bets:
            conf = bet.confidence_avg
            
            # Find which bucket this belongs to
            for low, high in buckets:
                if low <= conf < high:
                    bucket_key = f"{low}-{high}%"
                    confidence_performance[bucket_key]['bets'] += 1
                    confidence_performance[bucket_key]['wins'] += 1 if bet.outcome == 'win' else 0
                    confidence_performance[bucket_key]['losses'] += 1 if bet.outcome == 'loss' else 0
                    confidence_performance[bucket_key]['total_staked'] += bet.stake
                    confidence_performance[bucket_key]['total_profit'] += bet.actual_pnl
                    break
        
        # Calculate metrics
        results = {}
        for bucket, data in confidence_performance.items():
            if data['bets'] > 0:
                win_rate = (data['wins'] / data['bets']) * 100
                roi = (data['total_profit'] / data['total_staked']) * 100 if data['total_staked'] > 0 else 0
                
                results[bucket] = {
                    'confidence_range': bucket,
                    'total_bets': data['bets'],
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'win_rate': round(win_rate, 2),
                    'total_staked': round(data['total_staked'], 2),
                    'total_profit': round(data['total_profit'], 2),
                    'roi': round(roi, 2)
                }
        
        return results
    
    def find_best_prop_combinations(self, min_appearances: int = 10) -> List[Dict]:
        """
        Find best performing prop type combinations for parlays
        """
        self.logger.info("Finding best prop combinations")
        
        # Track prop combinations
        combinations = defaultdict(lambda: {
            'appearances': 0,
            'wins': 0,
            'total_profit': 0
        })
        
        for bet in self.bets:
            if bet.entry_size >= 2:
                # Create a sorted tuple of prop types
                combo = tuple(sorted(bet.prop_types))
                combinations[combo]['appearances'] += 1
                combinations[combo]['wins'] += 1 if bet.outcome == 'win' else 0
                combinations[combo]['total_profit'] += bet.actual_pnl
        
        # Filter by minimum appearances and calculate metrics
        results = []
        for combo, data in combinations.items():
            if data['appearances'] >= min_appearances:
                win_rate = (data['wins'] / data['appearances']) * 100
                avg_profit = data['total_profit'] / data['appearances']
                
                results.append({
                    'prop_combination': list(combo),
                    'appearances': data['appearances'],
                    'wins': data['wins'],
                    'win_rate': round(win_rate, 2),
                    'total_profit': round(data['total_profit'], 2),
                    'avg_profit': round(avg_profit, 2)
                })
        
        # Sort by win rate
        results.sort(key=lambda x: x['win_rate'], reverse=True)
        return results[:10]  # Top 10 combinations
    
    def calculate_optimal_entry_mix(self) -> Dict[int, float]:
        """
        Calculate optimal mix of entry sizes based on ROI
        """
        self.logger.info("Calculating optimal entry size mix")
        
        entry_analysis = self.analyze_by_entry_size()
        
        if not entry_analysis:
            return {}
        
        # Weight by ROI (positive ROIs only)
        total_weighted_roi = 0
        entry_weights = {}
        
        for size, data in entry_analysis.items():
            roi = data['roi']
            if roi > 0:
                entry_weights[size] = roi
                total_weighted_roi += roi
        
        # Calculate percentages
        optimal_mix = {}
        if total_weighted_roi > 0:
            for size, weight in entry_weights.items():
                optimal_mix[size] = round((weight / total_weighted_roi) * 100, 1)
        
        return optimal_mix
    
    def analyze_time_series(self, window_size: int = 7) -> List[Dict]:
        """
        Analyze performance over time with rolling windows
        """
        self.logger.info(f"Analyzing time series with {window_size}-bet window")
        
        if len(self.bets) < window_size:
            return []
        
        time_series = []
        
        for i in range(len(self.bets) - window_size + 1):
            window_bets = self.bets[i:i + window_size]
            
            wins = sum(1 for b in window_bets if b.outcome == 'win')
            win_rate = (wins / window_size) * 100
            total_profit = sum(b.actual_pnl for b in window_bets)
            
            time_series.append({
                'bet_number': i + window_size,
                'date': window_bets[-1].date.strftime('%Y-%m-%d'),
                'window_win_rate': round(win_rate, 2),
                'window_profit': round(total_profit, 2)
            })
        
        return time_series
    
    def calculate_risk_metrics(self) -> Dict:
        """
        Calculate comprehensive risk metrics
        """
        self.logger.info("Calculating risk metrics")
        
        if not self.bets:
            return {}
        
        returns = [b.actual_pnl / b.stake for b in self.bets]
        
        return {
            'volatility': round(np.std(returns), 4),
            'max_drawdown': self.result.max_drawdown,
            'sharpe_ratio': self.result.sharpe_ratio,
            'profit_factor': self.result.profit_factor,
            'avg_win': round(np.mean([b.actual_pnl for b in self.bets if b.outcome == 'win']), 2) if self.result.wins > 0 else 0,
            'avg_loss': round(np.mean([abs(b.actual_pnl) for b in self.bets if b.outcome == 'loss']), 2) if self.result.losses > 0 else 0,
            'win_loss_ratio': round(self.result.wins / self.result.losses, 2) if self.result.losses > 0 else 0,
            'longest_win_streak': self.result.longest_win_streak,
            'longest_loss_streak': self.result.longest_loss_streak
        }
    
    def generate_summary_report(self) -> Dict:
        """
        Generate a comprehensive summary report
        """
        self.logger.info("Generating summary report")
        
        return {
            'overall_performance': {
                'total_bets': self.result.total_bets,
                'wins': self.result.wins,
                'losses': self.result.losses,
                'win_rate': self.result.win_rate,
                'total_profit': self.result.total_profit,
                'total_staked': self.result.total_staked,
                'roi': self.result.roi,
                'starting_bankroll': self.result.starting_bankroll,
                'ending_bankroll': self.result.ending_bankroll
            },
            'by_entry_size': self.analyze_by_entry_size(),
            'by_prop_type': self.analyze_by_prop_type(),
            'by_sport': self.analyze_by_sport(),
            'by_confidence': self.analyze_by_confidence_level(),
            'best_prop_combinations': self.find_best_prop_combinations(),
            'optimal_entry_mix': self.calculate_optimal_entry_mix(),
            'risk_metrics': self.calculate_risk_metrics(),
            'daily_results': self.result.daily_results
        }
    
    def compare_to_baseline(self, baseline_result: BettingResult) -> Dict:
        """
        Compare performance to a baseline strategy
        """
        self.logger.info("Comparing to baseline")
        
        improvements = {}
        
        metrics = ['win_rate', 'roi', 'total_profit', 'sharpe_ratio']
        
        for metric in metrics:
            current = getattr(self.result, metric, 0)
            baseline = getattr(baseline_result, metric, 0)
            
            if baseline != 0:
                improvement = ((current - baseline) / baseline) * 100
                improvements[f'{metric}_improvement'] = round(improvement, 2)
            else:
                improvements[f'{metric}_improvement'] = 0
        
        return improvements
