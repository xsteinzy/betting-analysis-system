
"""
Backtesting API Functions
Functions to fetch backtest data for dashboard integration
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class BacktestingAPI:
    """
    API interface for dashboard to access backtesting results
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize API with database manager"""
        if db_manager is None:
            from database.db_manager import db_manager as default_db
            db_manager = default_db
        
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get_strategy_performance(
        self,
        strategy_name: Optional[str] = None,
        sport: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get overall strategy performance metrics
        
        Args:
            strategy_name: Filter by strategy name
            sport: Filter by sport (NBA/NFL)
            limit: Number of results to return
        
        Returns:
            List of strategy performance records
        """
        query = """
            SELECT 
                id,
                strategy_name,
                sport,
                entry_size,
                confidence_threshold,
                ev_threshold,
                start_date,
                end_date,
                total_bets,
                wins,
                losses,
                win_rate,
                total_profit,
                total_staked,
                roi,
                max_drawdown,
                sharpe_ratio,
                profit_factor,
                starting_bankroll,
                ending_bankroll,
                created_at
            FROM backtest_results
            WHERE 1=1
        """
        
        params = []
        
        if strategy_name:
            query += " AND strategy_name = %s"
            params.append(strategy_name)
        
        if sport:
            query += " AND sport = %s"
            params.append(sport)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = self.db.execute_query(query, tuple(params))
        return results
    
    def get_entry_size_analysis(self, backtest_id: Optional[int] = None) -> List[Dict]:
        """
        Get performance breakdown by entry size
        
        Args:
            backtest_id: Specific backtest to analyze, or latest if None
        
        Returns:
            List of entry size performance metrics
        """
        if backtest_id is None:
            # Get latest backtest
            backtest_id = self._get_latest_backtest_id()
        
        if backtest_id is None:
            return []
        
        # Query for entry size specific results
        query = """
            SELECT 
                entry_size,
                total_bets,
                wins,
                losses,
                win_rate,
                total_profit,
                roi,
                avg_bet_size
            FROM backtest_results
            WHERE id = %s OR (entry_size IS NOT NULL AND strategy_name = (
                SELECT strategy_name FROM backtest_results WHERE id = %s
            ))
            ORDER BY entry_size
        """
        
        results = self.db.execute_query(query, (backtest_id, backtest_id))
        return results
    
    def get_prop_type_performance(self, backtest_id: Optional[int] = None) -> Dict:
        """
        Get best performing prop types
        
        Args:
            backtest_id: Specific backtest to analyze, or latest if None
        
        Returns:
            Dict of prop type performance data
        """
        if backtest_id is None:
            backtest_id = self._get_latest_backtest_id()
        
        if backtest_id is None:
            return {}
        
        query = """
            SELECT 
                best_props,
                prop_performance
            FROM backtest_results
            WHERE id = %s
        """
        
        result = self.db.execute_query(query, (backtest_id,))
        
        if result:
            return {
                'best_props': result[0].get('best_props', []),
                'prop_performance': result[0].get('prop_performance', {})
            }
        
        return {}
    
    def get_sport_comparison(self) -> Dict:
        """
        Compare NBA vs NFL performance
        
        Returns:
            Dict with NBA and NFL performance metrics
        """
        query = """
            SELECT 
                sport,
                COUNT(*) as backtest_count,
                AVG(win_rate) as avg_win_rate,
                AVG(roi) as avg_roi,
                SUM(total_profit) as total_profit,
                AVG(sharpe_ratio) as avg_sharpe_ratio
            FROM backtest_results
            WHERE sport IS NOT NULL
            GROUP BY sport
        """
        
        results = self.db.execute_query(query)
        
        comparison = {}
        for row in results:
            sport = row['sport']
            comparison[sport] = {
                'backtest_count': row['backtest_count'],
                'avg_win_rate': round(float(row['avg_win_rate']), 2),
                'avg_roi': round(float(row['avg_roi']), 2),
                'total_profit': round(float(row['total_profit']), 2),
                'avg_sharpe_ratio': round(float(row['avg_sharpe_ratio']), 2)
            }
        
        return comparison
    
    def get_key_insights(self, backtest_id: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """
        Get top insights from backtests
        
        Args:
            backtest_id: Specific backtest, or latest if None
            limit: Number of insights to return
        
        Returns:
            List of key insights
        """
        if backtest_id is None:
            backtest_id = self._get_latest_backtest_id()
        
        if backtest_id is None:
            return []
        
        query = """
            SELECT 
                insights,
                strategy_name,
                win_rate,
                roi,
                created_at
            FROM backtest_results
            WHERE id = %s
        """
        
        result = self.db.execute_query(query, (backtest_id,))
        
        if result and result[0].get('insights'):
            insights = result[0]['insights']
            return insights[:limit]
        
        return []
    
    def get_historical_chart_data(
        self,
        backtest_id: Optional[int] = None,
        chart_type: str = 'cumulative_pl'
    ) -> List[Dict]:
        """
        Get data for charting
        
        Args:
            backtest_id: Specific backtest, or latest if None
            chart_type: Type of chart ('cumulative_pl', 'win_rate', 'bankroll')
        
        Returns:
            List of data points for charting
        """
        if backtest_id is None:
            backtest_id = self._get_latest_backtest_id()
        
        if backtest_id is None:
            return []
        
        query = """
            SELECT daily_results
            FROM backtest_results
            WHERE id = %s
        """
        
        result = self.db.execute_query(query, (backtest_id,))
        
        if not result or not result[0].get('daily_results'):
            return []
        
        daily_results = result[0]['daily_results']
        
        # Format based on chart type
        if chart_type == 'cumulative_pl':
            return [
                {
                    'date': day['date'],
                    'value': day['cumulative_pnl']
                }
                for day in daily_results
            ]
        
        elif chart_type == 'win_rate':
            # Calculate rolling win rate
            window_size = 10
            chart_data = []
            
            for i, day in enumerate(daily_results):
                if i >= window_size - 1:
                    window = daily_results[max(0, i - window_size + 1):i + 1]
                    total_bets = sum(d['bets'] for d in window)
                    total_wins = sum(d['wins'] for d in window)
                    win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0
                    
                    chart_data.append({
                        'date': day['date'],
                        'value': round(win_rate, 2)
                    })
            
            return chart_data
        
        elif chart_type == 'bankroll':
            return [
                {
                    'date': day['date'],
                    'value': day['bankroll']
                }
                for day in daily_results
            ]
        
        return daily_results
    
    def get_backtest_summary(self) -> Dict:
        """
        Get overall backtesting summary statistics
        
        Returns:
            Summary statistics across all backtests
        """
        query = """
            SELECT 
                COUNT(*) as total_backtests,
                SUM(total_bets) as total_bets,
                SUM(wins) as total_wins,
                SUM(losses) as total_losses,
                AVG(win_rate) as avg_win_rate,
                SUM(total_profit) as total_profit,
                AVG(roi) as avg_roi,
                MAX(roi) as best_roi,
                MIN(roi) as worst_roi,
                AVG(sharpe_ratio) as avg_sharpe_ratio
            FROM backtest_results
        """
        
        result = self.db.execute_query(query)
        
        if result:
            row = result[0]
            return {
                'total_backtests': row['total_backtests'],
                'total_bets': row['total_bets'],
                'total_wins': row['total_wins'],
                'total_losses': row['total_losses'],
                'avg_win_rate': round(float(row['avg_win_rate'] or 0), 2),
                'total_profit': round(float(row['total_profit'] or 0), 2),
                'avg_roi': round(float(row['avg_roi'] or 0), 2),
                'best_roi': round(float(row['best_roi'] or 0), 2),
                'worst_roi': round(float(row['worst_roi'] or 0), 2),
                'avg_sharpe_ratio': round(float(row['avg_sharpe_ratio'] or 0), 2)
            }
        
        return {}
    
    def get_best_strategies(self, metric: str = 'roi', limit: int = 5) -> List[Dict]:
        """
        Get best performing strategies
        
        Args:
            metric: Metric to sort by ('roi', 'win_rate', 'sharpe_ratio', 'total_profit')
            limit: Number of strategies to return
        
        Returns:
            List of best performing strategies
        """
        valid_metrics = ['roi', 'win_rate', 'sharpe_ratio', 'total_profit']
        if metric not in valid_metrics:
            metric = 'roi'
        
        query = f"""
            SELECT 
                strategy_name,
                sport,
                entry_size,
                confidence_threshold,
                win_rate,
                roi,
                total_profit,
                sharpe_ratio,
                total_bets,
                created_at
            FROM backtest_results
            ORDER BY {metric} DESC
            LIMIT %s
        """
        
        results = self.db.execute_query(query, (limit,))
        return results
    
    def get_strategy_evolution(self, strategy_name: str) -> List[Dict]:
        """
        Track how a strategy has performed over time
        
        Args:
            strategy_name: Name of strategy to track
        
        Returns:
            List of performance records over time
        """
        query = """
            SELECT 
                id,
                start_date,
                end_date,
                win_rate,
                roi,
                total_profit,
                sharpe_ratio,
                total_bets,
                created_at
            FROM backtest_results
            WHERE strategy_name = %s
            ORDER BY created_at ASC
        """
        
        results = self.db.execute_query(query, (strategy_name,))
        return results
    
    def _get_latest_backtest_id(self) -> Optional[int]:
        """Get ID of most recent backtest"""
        query = """
            SELECT id FROM backtest_results
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        result = self.db.execute_query(query)
        if result:
            return result[0]['id']
        
        return None


# Convenience functions for direct use

def get_strategy_performance(strategy_name=None, sport=None, limit=10):
    """Get strategy performance (convenience function)"""
    api = BacktestingAPI()
    return api.get_strategy_performance(strategy_name, sport, limit)


def get_entry_size_analysis(backtest_id=None):
    """Get entry size analysis (convenience function)"""
    api = BacktestingAPI()
    return api.get_entry_size_analysis(backtest_id)


def get_prop_type_performance(backtest_id=None):
    """Get prop type performance (convenience function)"""
    api = BacktestingAPI()
    return api.get_prop_type_performance(backtest_id)


def get_sport_comparison():
    """Get sport comparison (convenience function)"""
    api = BacktestingAPI()
    return api.get_sport_comparison()


def get_key_insights(backtest_id=None, limit=5):
    """Get key insights (convenience function)"""
    api = BacktestingAPI()
    return api.get_key_insights(backtest_id, limit)


def get_historical_chart_data(backtest_id=None, chart_type='cumulative_pl'):
    """Get chart data (convenience function)"""
    api = BacktestingAPI()
    return api.get_historical_chart_data(backtest_id, chart_type)


def get_backtest_summary():
    """Get backtest summary (convenience function)"""
    api = BacktestingAPI()
    return api.get_backtest_summary()


def get_best_strategies(metric='roi', limit=5):
    """Get best strategies (convenience function)"""
    api = BacktestingAPI()
    return api.get_best_strategies(metric, limit)

