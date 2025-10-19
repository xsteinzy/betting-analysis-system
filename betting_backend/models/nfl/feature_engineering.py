
"""
Feature engineering for NFL ML models
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


class NFLFeatureEngineer:
    """Feature engineering for NFL predictions"""
    
    def __init__(self):
        self.stats_calculator = StatsCalculator()
        self.trend_analyzer = TrendAnalyzer()
        self.opponent_analyzer = OpponentAnalyzer()
    
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
                SELECT pgs.*, g.date, g.home_team_id, g.away_team_id, g.week
                FROM player_game_stats pgs
                JOIN games g ON pgs.game_id = g.id
                WHERE pgs.player_id = %s 
                AND g.status = 'completed'
                AND g.id != %s
                AND g.sport = 'NFL'
                ORDER BY g.date DESC
                LIMIT 50
            """
            stats_list = db_manager.execute_query(query, (player_id, game_id))
            
            if not stats_list or len(stats_list) < 3:
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
            
            if len(stat_values) < 3:
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
            # NFL typically has 7 days between games (weekly schedule)
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
                    features['days_rest'] = 6  # Default for NFL (typical week)
            else:
                features['days_rest'] = 6  # Default
            
            # Games in last 4 weeks (NFL is weekly)
            if len(stats_list) >= 1:
                last_4_weeks = [s for s in stats_list[:4]]
                features['games_played_last_4_weeks'] = len(last_4_weeks)
            else:
                features['games_played_last_4_weeks'] = 0
            
            # Trend analysis
            if len(stat_values) >= 3:
                # Simple linear trend (slope)
                x = np.arange(min(5, len(stat_values)))
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
            if len(stat_values) >= 5:
                features['std_dev_last_5'] = np.std(stat_values[:5])
                mean_val = np.mean(stat_values[:5])
                if mean_val > 0:
                    cv = features['std_dev_last_5'] / mean_val
                    features['consistency_score'] = max(0, min(100, 100 - (cv * 100)))
                else:
                    features['consistency_score'] = 50.0
            else:
                features['std_dev_last_5'] = np.std(stat_values)
                features['consistency_score'] = 50.0
            
            # Snaps played (important predictor for NFL)
            # NFL uses "snaps" instead of "minutes"
            snaps_values = []
            for stat in stats_list[:10]:
                if 'stats' in stat:
                    # Try to get snaps, if not available use a proxy
                    snaps = stat['stats'].get('snaps', stat['stats'].get('offensive_snaps'))
                    if snaps is not None:
                        snaps_values.append(float(snaps))
            
            if snaps_values:
                features['avg_snaps_3_games'] = np.mean(snaps_values[:3]) if len(snaps_values) >= 3 else np.mean(snaps_values)
                features['avg_snaps_5_games'] = np.mean(snaps_values[:5]) if len(snaps_values) >= 5 else np.mean(snaps_values)
            else:
                # Default values if snaps not available
                features['avg_snaps_3_games'] = 50.0  # Default
                features['avg_snaps_5_games'] = 50.0  # Default
            
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
            import traceback
            traceback.print_exc()
            return None
    
    def prepare_training_data(self, db_manager, target_stat: str, 
                            min_games: int = 5) -> Optional[tuple]:
        """
        Prepare training data for a specific stat
        
        Args:
            db_manager: Database manager instance
            target_stat: The stat to predict
            min_games: Minimum games required for a player (NFL has fewer games)
            
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
                    g.status,
                    g.week
                FROM player_game_stats pgs
                JOIN games g ON pgs.game_id = g.id
                WHERE g.sport = 'NFL'
                AND g.status = 'completed'
                ORDER BY g.date DESC
                LIMIT 10000
            """
            
            all_stats = db_manager.execute_query(query)
            
            if not all_stats:
                logger.error("No player stats found in database for NFL")
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
                    # Skip if we don't have enough history (need at least 3 prior games for NFL)
                    if i < 3:
                        continue
                    
                    # Get target value
                    if 'stats' not in game or target_stat not in game['stats']:
                        continue
                    
                    target_value = game['stats'].get(target_stat)
                    if target_value is None:
                        continue
                    
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
