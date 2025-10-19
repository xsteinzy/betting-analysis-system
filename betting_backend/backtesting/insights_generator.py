"""
Insights Generator
Generates actionable insights from backtesting results
"""

import logging
from typing import Dict, List
from .performance_analyzer import PerformanceAnalyzer
from .strategy_simulator import BettingResult
from .config import INSIGHTS_CONFIG

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """
    Generates human-readable, actionable insights from backtesting results
    """
    
    def __init__(self, analyzer: PerformanceAnalyzer):
        """Initialize with a PerformanceAnalyzer"""
        self.analyzer = analyzer
        self.result = analyzer.result
        self.logger = logging.getLogger(__name__)
        self.insights = []
    
    def generate_all_insights(self) -> List[Dict]:
        """
        Generate all available insights
        """
        self.logger.info("Generating comprehensive insights")
        
        self.insights = []
        
        # Only generate insights if we have enough data
        if self.result.total_bets < INSIGHTS_CONFIG['min_sample_size']:
            self.insights.append({
                'type': 'warning',
                'title': 'Insufficient Data',
                'message': f"Only {self.result.total_bets} bets analyzed. Need at least {INSIGHTS_CONFIG['min_sample_size']} for reliable insights.",
                'priority': 'high'
            })
            return self.insights
        
        # Generate different types of insights
        self._generate_overall_performance_insights()
        self._generate_entry_size_insights()
        self._generate_prop_type_insights()
        self._generate_sport_insights()
        self._generate_confidence_insights()
        self._generate_bankroll_insights()
        self._generate_risk_insights()
        self._generate_strategic_recommendations()
        
        # Sort by priority and return top insights
        self.insights.sort(key=lambda x: self._priority_score(x), reverse=True)
        return self.insights[:INSIGHTS_CONFIG['top_insights_count']]
    
    def _generate_overall_performance_insights(self):
        """Generate insights about overall performance"""
        win_rate = self.result.win_rate
        roi = self.result.roi
        total_profit = self.result.total_profit
        
        # Win rate insights
        if win_rate >= 60:
            self.insights.append({
                'type': 'success',
                'title': 'Strong Win Rate',
                'message': f"Your strategy achieved a {win_rate}% win rate, which is excellent for sports betting.",
                'metric': win_rate,
                'priority': 'high'
            })
        elif win_rate >= 50:
            self.insights.append({
                'type': 'info',
                'title': 'Positive Win Rate',
                'message': f"Win rate of {win_rate}% is above 50%, showing promise with room for improvement.",
                'metric': win_rate,
                'priority': 'medium'
            })
        else:
            self.insights.append({
                'type': 'warning',
                'title': 'Low Win Rate',
                'message': f"Win rate of {win_rate}% needs improvement. Consider tightening filters or adjusting strategy.",
                'metric': win_rate,
                'priority': 'high'
            })
        
        # ROI insights
        if roi >= 15:
            self.insights.append({
                'type': 'success',
                'title': 'Excellent ROI',
                'message': f"ROI of {roi}% is outstanding. This strategy is highly profitable.",
                'metric': roi,
                'priority': 'high'
            })
        elif roi >= 5:
            self.insights.append({
                'type': 'success',
                'title': 'Positive ROI',
                'message': f"ROI of {roi}% is profitable. Continue with this approach.",
                'metric': roi,
                'priority': 'medium'
            })
        elif roi > 0:
            self.insights.append({
                'type': 'info',
                'title': 'Marginal Profit',
                'message': f"ROI of {roi}% is slightly profitable but could be improved.",
                'metric': roi,
                'priority': 'medium'
            })
        else:
            self.insights.append({
                'type': 'warning',
                'title': 'Negative ROI',
                'message': f"ROI of {roi}% indicates losses. Strategy needs significant adjustment.",
                'metric': roi,
                'priority': 'high'
            })
        
        # Profitability
        if total_profit > 0:
            self.insights.append({
                'type': 'success',
                'title': 'Net Profit Achieved',
                'message': f"Total profit of ${total_profit:.2f} from {self.result.total_bets} bets.",
                'metric': total_profit,
                'priority': 'high'
            })
    
    def _generate_entry_size_insights(self):
        """Generate insights about entry size performance"""
        entry_analysis = self.analyzer.analyze_by_entry_size()
        
        if not entry_analysis:
            return
        
        # Find best performing entry size
        best_entry = max(entry_analysis.items(), key=lambda x: x[1]['roi'])
        best_size, best_data = best_entry
        
        if best_data['roi'] > 0:
            self.insights.append({
                'type': 'success',
                'title': f'{best_size}-Pick Entries Perform Best',
                'message': f"{best_size}-pick entries have the highest ROI at {best_data['roi']}% with a {best_data['win_rate']}% win rate.",
                'metric': best_data['roi'],
                'priority': 'high',
                'recommendation': f"Focus on {best_size}-pick entries for optimal returns."
            })
        
        # Compare 2-picks vs larger entries
        if 2 in entry_analysis and len(entry_analysis) > 1:
            two_pick_wr = entry_analysis[2]['win_rate']
            avg_other_wr = sum(d['win_rate'] for s, d in entry_analysis.items() if s != 2) / (len(entry_analysis) - 1)
            
            if two_pick_wr > avg_other_wr + INSIGHTS_CONFIG['comparison_threshold']:
                self.insights.append({
                    'type': 'info',
                    'title': '2-Pick Entries More Consistent',
                    'message': f"2-pick entries have {two_pick_wr}% win rate vs {avg_other_wr:.1f}% average for larger entries.",
                    'priority': 'medium',
                    'recommendation': "Consider 2-picks for more consistent wins, though with lower payouts."
                })
        
        # Optimal mix recommendation
        optimal_mix = self.analyzer.calculate_optimal_entry_mix()
        if optimal_mix:
            mix_str = ", ".join([f"{pct}% {size}-pick" for size, pct in sorted(optimal_mix.items())])
            self.insights.append({
                'type': 'info',
                'title': 'Optimal Entry Size Mix',
                'message': f"Based on ROI, optimal allocation: {mix_str}",
                'priority': 'medium',
                'recommendation': "Diversify across entry sizes using this ratio."
            })
    
    def _generate_prop_type_insights(self):
        """Generate insights about prop type performance"""
        prop_analysis = self.analyzer.analyze_by_prop_type()
        
        if not prop_analysis:
            return
        
        # Get top 3 performing props
        sorted_props = sorted(prop_analysis.items(), key=lambda x: x[1]['win_rate'], reverse=True)
        top_props = sorted_props[:3]
        
        if top_props:
            top_prop_names = [p[0] for p in top_props]
            top_prop_wr = top_props[0][1]['win_rate']
            
            self.insights.append({
                'type': 'success',
                'title': 'Best Performing Props',
                'message': f"{', '.join(top_prop_names[:2])} have the highest win rates ({top_prop_wr}%+).",
                'priority': 'high',
                'recommendation': f"Prioritize {' and '.join(top_prop_names[:2])} props in your entries."
            })
        
        # Find prop combinations
        best_combos = self.analyzer.find_best_prop_combinations()
        if best_combos:
            best_combo = best_combos[0]
            combo_str = " + ".join(best_combo['prop_combination'])
            
            self.insights.append({
                'type': 'success',
                'title': 'Winning Prop Combination',
                'message': f"{combo_str} combination has {best_combo['win_rate']}% win rate across {best_combo['appearances']} bets.",
                'priority': 'high',
                'recommendation': f"Use {combo_str} together in parlays for best results."
            })
        
        # Find underperforming props
        if len(sorted_props) >= 3:
            worst_props = sorted_props[-3:]
            worst_prop_names = [p[0] for p in worst_props if p[1]['win_rate'] < 45]
            
            if worst_prop_names:
                self.insights.append({
                    'type': 'warning',
                    'title': 'Underperforming Props',
                    'message': f"{', '.join(worst_prop_names)} have low win rates. Consider avoiding these.",
                    'priority': 'medium',
                    'recommendation': f"Filter out {', '.join(worst_prop_names)} to improve overall performance."
                })
    
    def _generate_sport_insights(self):
        """Generate insights about sport-specific performance"""
        sport_analysis = self.analyzer.analyze_by_sport()
        
        if len(sport_analysis) < 2:
            return
        
        # Compare NBA vs NFL
        if 'NBA' in sport_analysis and 'NFL' in sport_analysis:
            nba = sport_analysis['NBA']
            nfl = sport_analysis['NFL']
            
            wr_diff = nba['win_rate'] - nfl['win_rate']
            roi_diff = nba['roi'] - nfl['roi']
            
            if abs(wr_diff) > INSIGHTS_CONFIG['comparison_threshold']:
                better_sport = 'NBA' if wr_diff > 0 else 'NFL'
                worse_sport = 'NFL' if wr_diff > 0 else 'NBA'
                
                self.insights.append({
                    'type': 'info',
                    'title': f'{better_sport} Outperforms {worse_sport}',
                    'message': f"{better_sport} props have {abs(wr_diff):.1f}% higher win rate than {worse_sport} ({sport_analysis[better_sport]['win_rate']}% vs {sport_analysis[worse_sport]['win_rate']}%).",
                    'priority': 'high',
                    'recommendation': f"Allocate more bankroll to {better_sport} props for better returns."
                })
            
            # Bankroll allocation recommendation
            total_bets = nba['total_bets'] + nfl['total_bets']
            if nba['roi'] > 0 and nfl['roi'] > 0:
                nba_weight = (nba['roi'] / (nba['roi'] + nfl['roi'])) * 100
                nfl_weight = 100 - nba_weight
                
                self.insights.append({
                    'type': 'info',
                    'title': 'Optimal Sport Allocation',
                    'message': f"Based on ROI, allocate {nba_weight:.0f}% to NBA and {nfl_weight:.0f}% to NFL.",
                    'priority': 'medium',
                    'recommendation': "Adjust your betting splits between sports accordingly."
                })
    
    def _generate_confidence_insights(self):
        """Generate insights about confidence thresholds"""
        confidence_analysis = self.analyzer.analyze_by_confidence_level()
        
        if not confidence_analysis:
            return
        
        # Find best performing confidence range
        sorted_conf = sorted(confidence_analysis.items(), key=lambda x: x[1]['win_rate'], reverse=True)
        
        if sorted_conf:
            best_range, best_data = sorted_conf[0]
            
            self.insights.append({
                'type': 'info',
                'title': f'Confidence Sweet Spot: {best_range}',
                'message': f"Bets with {best_range} confidence have the best win rate at {best_data['win_rate']}%.",
                'priority': 'high',
                'recommendation': f"Focus on bets with confidence in the {best_range} range."
            })
        
        # Check if higher confidence = better performance
        if len(sorted_conf) >= 3:
            low_conf = next((v for k, v in sorted_conf if '60-70' in k), None)
            high_conf = next((v for k, v in sorted_conf if '80-90' in k or '90-100' in k), None)
            
            if low_conf and high_conf:
                conf_diff = high_conf['win_rate'] - low_conf['win_rate']
                
                if conf_diff > INSIGHTS_CONFIG['comparison_threshold']:
                    self.insights.append({
                        'type': 'success',
                        'title': 'Higher Confidence Improves Results',
                        'message': f"High confidence bets outperform low confidence by {conf_diff:.1f}% in win rate.",
                        'priority': 'high',
                        'recommendation': "Set minimum confidence threshold at 75%+ for better results."
                    })
    
    def _generate_bankroll_insights(self):
        """Generate insights about bankroll management"""
        starting = self.result.starting_bankroll
        ending = self.result.ending_bankroll
        max_dd = self.result.max_drawdown
        
        # Drawdown warning
        if max_dd > 30:
            self.insights.append({
                'type': 'warning',
                'title': 'High Drawdown Risk',
                'message': f"Maximum drawdown of {max_dd}% is concerning. Reduce bet sizes or tighten filters.",
                'metric': max_dd,
                'priority': 'high',
                'recommendation': "Use smaller bet sizes (1-2% of bankroll) to reduce risk."
            })
        elif max_dd > 20:
            self.insights.append({
                'type': 'info',
                'title': 'Moderate Drawdown',
                'message': f"Maximum drawdown of {max_dd}% is acceptable but monitor closely.",
                'metric': max_dd,
                'priority': 'medium'
            })
        
        # Bankroll growth
        growth_pct = ((ending - starting) / starting) * 100
        
        if growth_pct > 20:
            self.insights.append({
                'type': 'success',
                'title': 'Strong Bankroll Growth',
                'message': f"Bankroll grew {growth_pct:.1f}% from ${starting:.2f} to ${ending:.2f}.",
                'priority': 'high'
            })
    
    def _generate_risk_insights(self):
        """Generate insights about risk metrics"""
        risk_metrics = self.analyzer.calculate_risk_metrics()
        
        sharpe = self.result.sharpe_ratio
        profit_factor = self.result.profit_factor
        
        # Sharpe ratio insights
        if sharpe > 2:
            self.insights.append({
                'type': 'success',
                'title': 'Excellent Risk-Adjusted Returns',
                'message': f"Sharpe ratio of {sharpe:.2f} indicates exceptional risk-adjusted performance.",
                'priority': 'medium'
            })
        elif sharpe > 1:
            self.insights.append({
                'type': 'success',
                'title': 'Good Risk-Adjusted Returns',
                'message': f"Sharpe ratio of {sharpe:.2f} shows good returns relative to risk taken.",
                'priority': 'medium'
            })
        
        # Profit factor insights
        if profit_factor > 2:
            self.insights.append({
                'type': 'success',
                'title': 'Strong Profit Factor',
                'message': f"Profit factor of {profit_factor:.2f} means wins are {profit_factor:.1f}x larger than losses.",
                'priority': 'medium'
            })
        
        # Win/loss streaks
        if risk_metrics.get('longest_loss_streak', 0) > 8:
            self.insights.append({
                'type': 'warning',
                'title': 'Long Losing Streaks',
                'message': f"Longest losing streak of {risk_metrics['longest_loss_streak']} bets. Be prepared for variance.",
                'priority': 'medium',
                'recommendation': "Maintain proper bankroll to weather losing streaks."
            })
    
    def _generate_strategic_recommendations(self):
        """Generate high-level strategic recommendations"""
        
        # Sample size recommendation
        if self.result.total_bets < 100:
            self.insights.append({
                'type': 'info',
                'title': 'Increase Sample Size',
                'message': f"With only {self.result.total_bets} bets, run more backtests for statistical confidence.",
                'priority': 'low',
                'recommendation': "Test on at least 100+ bets before committing real money."
            })
        
        # Overall recommendation
        if self.result.roi > 10 and self.result.win_rate > 55:
            self.insights.append({
                'type': 'success',
                'title': 'Strategy Ready for Live Betting',
                'message': "Strong performance metrics suggest this strategy is viable for real betting.",
                'priority': 'high',
                'recommendation': "Start with small stakes and gradually scale up as you validate results."
            })
        elif self.result.roi > 0:
            self.insights.append({
                'type': 'info',
                'title': 'Strategy Shows Promise',
                'message': "Positive ROI but needs further optimization before heavy betting.",
                'priority': 'high',
                'recommendation': "Test with minimal stakes while refining the approach."
            })
        else:
            self.insights.append({
                'type': 'warning',
                'title': 'Strategy Needs Improvement',
                'message': "Negative returns indicate strategy needs significant changes.",
                'priority': 'high',
                'recommendation': "Review filters, prop selection, and entry sizes before betting real money."
            })
    
    def _priority_score(self, insight: Dict) -> int:
        """Calculate priority score for sorting insights"""
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        type_map = {'warning': 3, 'success': 2, 'info': 1}
        
        priority_score = priority_map.get(insight.get('priority', 'low'), 1)
        type_score = type_map.get(insight.get('type', 'info'), 1)
        
        return priority_score * 10 + type_score
    
    def get_key_insights(self, limit: int = 5) -> List[Dict]:
        """Get top N key insights"""
        if not self.insights:
            self.generate_all_insights()
        
        return self.insights[:limit]
    
    def format_for_display(self) -> str:
        """Format insights as readable text"""
        if not self.insights:
            self.generate_all_insights()
        
        output = ["=== BACKTESTING INSIGHTS ===\n"]
        
        for i, insight in enumerate(self.insights, 1):
            output.append(f"{i}. [{insight['type'].upper()}] {insight['title']}")
            output.append(f"   {insight['message']}")
            if 'recommendation' in insight:
                output.append(f"   → {insight['recommendation']}")
            output.append("")
        
        return "\n".join(output)
