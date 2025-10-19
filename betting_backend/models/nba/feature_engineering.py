
"""
Feature engineering for NBA ML models
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

# Import from existing utilities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from data_processing.stats_calculator import StatsCalculator, TrendAnalyzer, OpponentAnalyzer

logger = logging.getLogger(__name__)


class NBAFeatureEngineer:
    """Feature engineering for NBA predictions"""
    
    def __init__(self):
        self.stats_calculator = StatsCalculator()
        self.trend_analyzer = TrendAnalyzer()
        self.opponent_analyzer = OpponentAnalyzer()
    
    def calculate_double_double(self, stats: Dict[str, Any]) -> int:
        """Calculate if a game was a double-double (1) or not (0)"""
        points = stats.get('points', 0) or 0
        rebounds = stats.get('rebounds', 0) or 0
        assists = stats.get('assists', 0) or 0
        
        count = 0
        if points >= 10:
            count += 1
        if rebounds >= 10:
            count += 1
        if assists >= 10:
            count += 1
        
        return 1 if count >= 2 else 0
    
    def extract_features_for_player(self, player_id: int, game_id: int, 
                                   db_manager, is_home: bool,
                                   target_stat: str) -> Optional[Dict[str, float]]:
        """
        Extract features for a single player for a specific game
        
        Args:
            player_id: Player ID
            game_id: Game ID for prediction
            db_manager: Database manager instance
            is_home: Whether player is playing at home
            target_stat: The stat we're predicting
            
        Returns:
            Dictionary of features or None if insufficient data
        """
        try:
            # Get player's recent stats (exclude current game if it exists)
            query = """
                SELECT pgs.*, g.date, g.home_team_id, g.away_team_id
                FROM player_game_stats pgs
                JOIN games g ON pgs.game_id = g.id
                WHERE pgs.player_id = %s 
                AND g.status = 'completed'
                AND g.id != %s
                ORDER BY g.date DESC
                LIMIT 50
            """
            stats_list = db_manager.execute_query(query, (player_id, game_id))
            
            if not stats_list or len(stats_list) < 5:
                logger.warning(f"Insufficient data for player {player_id}: only {len(stats_list) if stats_list else 0} games")
                return None
            
            # Initialize features
            features = {}
            
            # Extract stat values from JSONB
            stat_values = []
            for stat in stats_list:
                if 'stats' in stat and target_stat in stat['stats']:
                    value = stat['stats'].get(target_stat)
                    if value is not None:
                        stat_values.append(float(value))
            
            if len(stat_values) < 5:
                logger.warning(f"Insufficient {target_stat} data for player {player_id}")
                return None
            
            # Rolling averages
            features['avg_3_games'] = np.mean(stat_values[:3]) if len(stat_values) >= 3 else np.mean(stat_values)
            features['avg_5_games'] = np.mean(stat_values[:5]) if len(stat_values) >= 5 else np.mean(stat_values)
            features['avg_10_games'] = np.mean(stat_values[:10]) if len(stat_values) >= 10 else np.mean(stat_values)
            
            # Season average
            features['season_avg'] = np.mean(stat_values)
            features['games_played_this_season'] = len(stat_values)
            
            # Home/away splits
            home_stats = [s for s in stats_list if s.get('is_home', False)]
            away_stats = [s for s in stats_list if not s.get('is_home', False)]
            
            home_values = [float(s['stats'].get(target_stat, 0)) for s in home_stats if 'stats' in s and target_stat in s['stats'] and s['stats'].get(target_stat) is not None]
            away_values = [float(s['stats'].get(target_stat, 0)) for s in away_stats if 'stats' in s and target_stat in s['stats'] and s['stats'].get(target_stat) is not None]
            
            features['home_avg'] = np.mean(home_values) if home_values else features['season_avg']
            features['away_avg'] = np.mean(away_values) if away_values else features['season_avg']
            features['is_home'] = 1.0 if is_home else 0.0
            
            # Rest days (calculate from most recent game)
            if len(stats_list) >= 1:
                last_game_date = stats_list[0]['date']
                # Get current game date
                current_game_query = "SELECT date FROM games WHERE id = %s"
                current_game = db_manager.execute_query(current_game_query, (game_id,))
                if current_game:
                    current_date = current_game[0]['date']
                    if isinstance(current_date, str):
                        current_date = datetime.strptime(current_date[:10], '%Y-%m-%d').date()
                    if isinstance(last_game_date, str):
                        last_game_date = datetime.strptime(last_game_date[:10], '%Y-%m-%d').date()
                    features['days_rest'] = max(0, (current_date - last_game_date).days - 1)
                else:
                    features['days_rest'] = 2  # Default
            else:
                features['days_rest'] = 2  # Default
            
            # Games in last 7 days
            if len(stats_list) >= 1:
                last_7_days = [s for s in stats_list[:7]]
                features['games_played_last_7_days'] = len(last_7_days)
            else:
                features['games_played_last_7_days'] = 0
            
            # Trend analysis
            if len(stat_values) >= 5:
                # Simple linear trend (slope)
                x = np.arange(min(10, len(stat_values)))
                y = stat_values[:len(x)]
                if len(x) > 1 and len(y) > 1:
                    try:
                        slope = np.polyfit(x, y, 1)[0]
                        features['recent_trend'] = slope
                    except:
                        features['recent_trend'] = 0.0
                else:
                    features['recent_trend'] = 0.0
            else:
                features['recent_trend'] = 0.0
            
            # Consistency metrics
            if len(stat_values) >= 10:
                features['std_dev_last_10'] = np.std(stat_values[:10])
                mean_val = np.mean(stat_values[:10])
                if mean_val > 0:
                    cv = features['std_dev_last_10'] / mean_val
                    features['consistency_score'] = max(0, min(100, 100 - (cv * 100)))
                else:
                    features['consistency_score'] = 50.0
            else:
                features['std_dev_last_10'] = np.std(stat_values)
                features['consistency_score'] = 50.0
            
            # Minutes played (important predictor)
            minutes_values = []
            for stat in stats_list[:10]:
                if 'stats' in stat and 'minutes' in stat['stats']:
                    minutes = stat['stats'].get('minutes')
                    if minutes is not None:
                        minutes_values.append(float(minutes))
            
            if minutes_values:
                features['avg_minutes_3_games'] = np.mean(minutes_values[:3]) if len(minutes_values) >= 3 else np.mean(minutes_values)
                features['avg_minutes_5_games'] = np.mean(minutes_values[:5]) if len(minutes_values) >= 5 else np.mean(minutes_values)
            else:
                features['avg_minutes_3_games'] = 30.0  # Default
                features['avg_minutes_5_games'] = 30.0  # Default
            
            # Opponent metrics (simplified - can be enhanced)
            features['opponent_defensive_rating'] = 100.0  # Placeholder
            features['matchup_history_avg'] = features['season_avg']  # Placeholder
            
            # Fill any missing values
            for key in features:
                if features[key] is None or np.isnan(features[key]):
                    features[key] = 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features for player {player_id}: {e}")
            return None
    
    def prepare_training_data(self, db_manager, target_stat: str, 
                            min_games: int = 10) -> Optional[tuple]:
        """
        Prepare training data for a specific stat
        
        Args:
            db_manager: Database manager instance
            target_stat: The stat to predict
            min_games: Minimum games required for a player
            
        Returns:
            Tuple of (features_df, targets, game_ids, player_ids) or None
        """
        try:
            logger.info(f"Preparing training data for {target_stat}...")
            
            # Get all completed games with player stats
            query = """
                SELECT 
                    pgs.player_id,
                    pgs.game_id,
                    pgs.is_home,
                    pgs.stats,
                    g.date,
                    g.status
                FROM player_game_stats pgs
                JOIN games g ON pgs.game_id = g.id
                WHERE g.sport = 'NBA'
                AND g.status = 'completed'
                ORDER BY g.date DESC
                LIMIT 10000
            """
            
            all_stats = db_manager.execute_query(query)
            
            if not all_stats:
                logger.error("No player stats found in database")
                return None
            
            logger.info(f"Found {len(all_stats)} player game stats")
            
            # Group by player to check minimum games
            player_games = defaultdict(list)
            for stat in all_stats:
                player_games[stat['player_id']].append(stat)
            
            # Filter players with minimum games
            valid_players = {
                player_id: games 
                for player_id, games in player_games.items() 
                if len(games) >= min_games
            }
            
            logger.info(f"Found {len(valid_players)} players with at least {min_games} games")
            
            # Extract features and targets
            features_list = []
            targets_list = []
            game_ids_list = []
            player_ids_list = []
            
            for player_id, games in valid_players.items():
                # Sort by date descending
                games = sorted(games, key=lambda x: x['date'], reverse=True)
                
                # For each game, use it as a training example
                for i, game in enumerate(games):
                    # Skip if we don't have enough history (need at least 5 prior games)
                    if i < 5:
                        continue
                    
                    # Get target value
                    if 'stats' not in game or target_stat not in game['stats']:
                        continue
                    
                    target_value = game['stats'].get(target_stat)
                    if target_value is None:
                        continue
                    
                    # Special handling for double_double
                    if target_stat == 'double_double':
                        target_value = self.calculate_double_double(game['stats'])
                    
                    # Extract features using only prior games
                    game_id = game['game_id']
                    is_home = game.get('is_home', False)
                    
                    features = self.extract_features_for_player(
                        player_id, game_id, db_manager, is_home, target_stat
                    )
                    
                    if features is not None:
                        features_list.append(features)
                        targets_list.append(float(target_value))
                        game_ids_list.append(game_id)
                        player_ids_list.append(player_id)
            
            if not features_list:
                logger.error(f"No training examples created for {target_stat}")
                return None
            
            # Convert to DataFrame
            features_df = pd.DataFrame(features_list)
            targets = np.array(targets_list)
            
            logger.info(f"Created {len(features_df)} training examples for {target_stat}")
            logger.info(f"Feature columns: {list(features_df.columns)}")
            logger.info(f"Target stats - Mean: {targets.mean():.2f}, Std: {targets.std():.2f}, Min: {targets.min():.2f}, Max: {targets.max():.2f}")
            
            return features_df, targets, game_ids_list, player_ids_list
            
        except Exception as e:
            logger.error(f"Error preparing training data for {target_stat}: {e}")
            import traceback
            traceback.print_exc()
            return None
