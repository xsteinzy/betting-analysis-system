
"""
Statistics calculation utilities for player performance analysis
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class StatsCalculator:
    """Calculate various statistics for player performance analysis"""
    
    @staticmethod
    def calculate_rolling_average(stats_list: List[Dict[str, Any]], 
                                 stat_key: str, 
                                 window: int = 5) -> Optional[float]:
        """
        Calculate rolling average for a specific stat
        
        Args:
            stats_list: List of stat dictionaries (most recent first)
            stat_key: Key for the stat to calculate (e.g., 'points', 'rebounds')
            window: Number of games to include in average
            
        Returns:
            Rolling average or None if insufficient data
        """
        try:
            values = []
            for stat in stats_list[:window]:
                if 'stats' in stat and stat_key in stat['stats']:
                    value = stat['stats'][stat_key]
                    if value is not None:
                        values.append(float(value))
            
            if len(values) >= min(3, window):  # Require at least 3 games or window size
                return round(statistics.mean(values), 2)
            
            return None
        except Exception as e:
            logger.error(f"Error calculating rolling average: {e}")
            return None
    
    @staticmethod
    def calculate_multiple_rolling_averages(stats_list: List[Dict[str, Any]], 
                                           stat_keys: List[str],
                                           windows: List[int] = [3, 5, 10]) -> Dict[str, Dict[int, float]]:
        """
        Calculate multiple rolling averages for multiple stats
        
        Args:
            stats_list: List of stat dictionaries (most recent first)
            stat_keys: List of stat keys to calculate
            windows: List of window sizes
            
        Returns:
            Dictionary with structure: {stat_key: {window: average}}
        """
        result = {}
        
        for stat_key in stat_keys:
            result[stat_key] = {}
            for window in windows:
                avg = StatsCalculator.calculate_rolling_average(stats_list, stat_key, window)
                if avg is not None:
                    result[stat_key][window] = avg
        
        return result
    
    @staticmethod
    def calculate_home_away_splits(stats_list: List[Dict[str, Any]], 
                                   stat_keys: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate home vs away performance splits
        
        Args:
            stats_list: List of stat dictionaries with is_home field
            stat_keys: List of stat keys to calculate
            
        Returns:
            Dictionary with home and away averages
        """
        home_stats = defaultdict(list)
        away_stats = defaultdict(list)
        
        for stat in stats_list:
            is_home = stat.get('is_home', False)
            stats_dict = stat.get('stats', {})
            
            for key in stat_keys:
                if key in stats_dict and stats_dict[key] is not None:
                    value = float(stats_dict[key])
                    if is_home:
                        home_stats[key].append(value)
                    else:
                        away_stats[key].append(value)
        
        result = {}
        for key in stat_keys:
            result[key] = {
                'home': {
                    'avg': round(statistics.mean(home_stats[key]), 2) if home_stats[key] else None,
                    'games': len(home_stats[key])
                },
                'away': {
                    'avg': round(statistics.mean(away_stats[key]), 2) if away_stats[key] else None,
                    'games': len(away_stats[key])
                }
            }
        
        return result
    
    @staticmethod
    def calculate_days_rest(game_dates: List[str]) -> List[int]:
        """
        Calculate days of rest between games
        
        Args:
            game_dates: List of game dates in ISO format or date objects (chronological order)
            
        Returns:
            List of days rest before each game (first game has 0)
        """
        if not game_dates:
            return []
        
        days_rest = [0]  # First game has no prior rest calculation
        
        for i in range(1, len(game_dates)):
            try:
                if isinstance(game_dates[i], str):
                    current_date = datetime.strptime(game_dates[i][:10], '%Y-%m-%d')
                    previous_date = datetime.strptime(game_dates[i-1][:10], '%Y-%m-%d')
                else:
                    current_date = game_dates[i]
                    previous_date = game_dates[i-1]
                
                rest_days = (current_date - previous_date).days - 1  # Subtract 1 to not count game day
                days_rest.append(max(0, rest_days))
            except Exception as e:
                logger.error(f"Error calculating days rest: {e}")
                days_rest.append(0)
        
        return days_rest
    
    @staticmethod
    def calculate_recent_form(stats_list: List[Dict[str, Any]], 
                             stat_key: str,
                             threshold: float,
                             window: int = 5) -> Dict[str, Any]:
        """
        Calculate recent form metrics
        
        Args:
            stats_list: List of stat dictionaries (most recent first)
            stat_key: Key for the stat to analyze
            threshold: Threshold value for "success"
            window: Number of recent games to analyze
            
        Returns:
            Dictionary with form metrics
        """
        try:
            recent_games = stats_list[:window]
            values = []
            hits = 0
            
            for stat in recent_games:
                if 'stats' in stat and stat_key in stat['stats']:
                    value = stat['stats'][stat_key]
                    if value is not None:
                        value = float(value)
                        values.append(value)
                        if value >= threshold:
                            hits += 1
            
            if not values:
                return None
            
            return {
                'games_analyzed': len(values),
                'average': round(statistics.mean(values), 2),
                'median': round(statistics.median(values), 2),
                'std_dev': round(statistics.stdev(values), 2) if len(values) > 1 else 0,
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'hit_rate': round(hits / len(values) * 100, 1),
                'threshold': threshold
            }
        except Exception as e:
            logger.error(f"Error calculating recent form: {e}")
            return None
    
    @staticmethod
    def calculate_consistency_score(stats_list: List[Dict[str, Any]], 
                                   stat_key: str,
                                   window: int = 10) -> Optional[float]:
        """
        Calculate consistency score (inverse of coefficient of variation)
        Lower variance = more consistent
        
        Args:
            stats_list: List of stat dictionaries (most recent first)
            stat_key: Key for the stat to analyze
            window: Number of games to analyze
            
        Returns:
            Consistency score (0-100, higher is more consistent)
        """
        try:
            values = []
            for stat in stats_list[:window]:
                if 'stats' in stat and stat_key in stat['stats']:
                    value = stat['stats'][stat_key]
                    if value is not None:
                        values.append(float(value))
            
            if len(values) < 3:
                return None
            
            mean_val = statistics.mean(values)
            if mean_val == 0:
                return 0
            
            std_dev = statistics.stdev(values)
            coefficient_of_variation = std_dev / mean_val
            
            # Convert to consistency score (0-100)
            # Lower CV = higher consistency
            consistency = max(0, min(100, 100 - (coefficient_of_variation * 100)))
            
            return round(consistency, 2)
        except Exception as e:
            logger.error(f"Error calculating consistency score: {e}")
            return None


class OpponentAnalyzer:
    """Analyze opponent defensive performance"""
    
    @staticmethod
    def calculate_opponent_defensive_ranking(opponent_stats: List[Dict[str, Any]], 
                                            stat_key: str,
                                            league_average: float) -> Dict[str, Any]:
        """
        Calculate opponent's defensive ranking for a specific stat
        
        Args:
            opponent_stats: List of opponent's defensive stats against position/player type
            stat_key: Stat to analyze (e.g., 'points_allowed', 'rebounds_allowed')
            league_average: League average for this stat
            
        Returns:
            Dictionary with defensive ranking metrics
        """
        try:
            values = []
            for stat in opponent_stats:
                if stat_key in stat and stat[stat_key] is not None:
                    values.append(float(stat[stat_key]))
            
            if not values:
                return None
            
            avg_allowed = statistics.mean(values)
            
            # Lower is better for defense (fewer points/stats allowed)
            # Calculate percentile (0 = best defense, 100 = worst defense)
            defensive_rating = round((avg_allowed / league_average) * 100, 1)
            
            return {
                'average_allowed': round(avg_allowed, 2),
                'league_average': league_average,
                'defensive_rating': defensive_rating,
                'games_analyzed': len(values),
                'favorable': defensive_rating > 105  # Opponent allows more than league average
            }
        except Exception as e:
            logger.error(f"Error calculating opponent defensive ranking: {e}")
            return None
    
    @staticmethod
    def get_matchup_history(player_stats: List[Dict[str, Any]], 
                           opponent_team_id: int,
                           stat_keys: List[str]) -> Dict[str, Any]:
        """
        Get player's historical performance against a specific opponent
        
        Args:
            player_stats: List of player's game stats with opponent info
            opponent_team_id: Opponent team ID to filter by
            stat_keys: Stats to analyze
            
        Returns:
            Dictionary with matchup history averages
        """
        matchup_games = [
            stat for stat in player_stats 
            if stat.get('opponent_team_id') == opponent_team_id
        ]
        
        if not matchup_games:
            return {'games': 0, 'note': 'No previous matchups found'}
        
        result = {'games': len(matchup_games)}
        
        for key in stat_keys:
            values = []
            for stat in matchup_games:
                if 'stats' in stat and key in stat['stats']:
                    value = stat['stats'][key]
                    if value is not None:
                        values.append(float(value))
            
            if values:
                result[key] = {
                    'average': round(statistics.mean(values), 2),
                    'max': round(max(values), 2),
                    'min': round(min(values), 2)
                }
        
        return result


class TrendAnalyzer:
    """Analyze statistical trends over time"""
    
    @staticmethod
    def calculate_trend(stats_list: List[Dict[str, Any]], 
                       stat_key: str,
                       window: int = 10) -> Dict[str, Any]:
        """
        Calculate trend direction for a stat (improving, declining, stable)
        
        Args:
            stats_list: List of stat dictionaries (most recent first)
            stat_key: Stat to analyze
            window: Number of games to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            values = []
            for stat in stats_list[:window]:
                if 'stats' in stat and stat_key in stat['stats']:
                    value = stat['stats'][stat_key]
                    if value is not None:
                        values.append(float(value))
            
            if len(values) < 5:
                return None
            
            # Reverse to get chronological order
            values = list(reversed(values))
            
            # Calculate simple linear trend
            n = len(values)
            x_mean = (n - 1) / 2
            y_mean = statistics.mean(values)
            
            numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(values))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
            
            # Determine trend
            if abs(slope) < 0.1:
                trend = 'stable'
            elif slope > 0:
                trend = 'improving'
            else:
                trend = 'declining'
            
            # Calculate recent vs early average
            half = n // 2
            recent_avg = statistics.mean(values[half:])
            early_avg = statistics.mean(values[:half])
            change_pct = ((recent_avg - early_avg) / early_avg * 100) if early_avg != 0 else 0
            
            return {
                'trend': trend,
                'slope': round(slope, 3),
                'recent_average': round(recent_avg, 2),
                'early_average': round(early_avg, 2),
                'change_percent': round(change_pct, 1),
                'games_analyzed': n
            }
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return None
    
    @staticmethod
    def detect_outliers(stats_list: List[Dict[str, Any]], 
                       stat_key: str,
                       window: int = 20) -> List[Dict[str, Any]]:
        """
        Detect statistical outliers in recent performance
        
        Args:
            stats_list: List of stat dictionaries (most recent first)
            stat_key: Stat to analyze
            window: Number of games to analyze
            
        Returns:
            List of outlier games
        """
        try:
            values = []
            games = []
            
            for i, stat in enumerate(stats_list[:window]):
                if 'stats' in stat and stat_key in stat['stats']:
                    value = stat['stats'][stat_key]
                    if value is not None:
                        values.append(float(value))
                        games.append((i, stat))
            
            if len(values) < 5:
                return []
            
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values)
            
            outliers = []
            for i, (game_idx, stat) in enumerate(games):
                value = values[i]
                z_score = (value - mean_val) / std_dev if std_dev != 0 else 0
                
                if abs(z_score) > 2:  # More than 2 standard deviations
                    outliers.append({
                        'game_index': game_idx,
                        'value': value,
                        'z_score': round(z_score, 2),
                        'type': 'high' if z_score > 0 else 'low',
                        'game_date': stat.get('game_date') or stat.get('date')
                    })
            
            return outliers
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return []
