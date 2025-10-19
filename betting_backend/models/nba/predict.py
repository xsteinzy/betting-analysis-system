
"""
NBA Prediction Engine
Generate predictions for upcoming games
"""
import logging
import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import project modules
from database.db_manager import db_manager
from utils.logger import setup_logger
from models.nba.config import (
    PROP_TYPES, MODEL_FILES, CONFIDENCE_CONFIG, MODEL_VERSION
)
from models.nba.feature_engineering import NBAFeatureEngineer

# Setup logger
logger = setup_logger('predict')


class NBAPredictor:
    """Generate predictions for NBA player props"""
    
    def __init__(self):
        self.feature_engineer = NBAFeatureEngineer()
        self.models = {}
        self.scalers = {}
        self.metadata = {}
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk"""
        logger.info("Loading trained models...")
        
        for prop_type in PROP_TYPES:
            try:
                model_files = MODEL_FILES[prop_type]
                
                # Check if models exist
                if not model_files['linear_regression'].exists():
                    logger.warning(f"Models for {prop_type} not found. Train models first.")
                    continue
                
                # Load models
                self.models[prop_type] = {
                    'linear_regression': joblib.load(model_files['linear_regression']),
                    'random_forest': joblib.load(model_files['random_forest']),
                    'gradient_boosting': joblib.load(model_files['gradient_boosting'])
                }
                
                # Load scaler
                self.scalers[prop_type] = joblib.load(model_files['scaler'])
                
                # Load metadata
                with open(model_files['metadata'], 'r') as f:
                    self.metadata[prop_type] = json.load(f)
                
                logger.info(f"✓ Loaded models for {prop_type}")
                
            except Exception as e:
                logger.error(f"Failed to load models for {prop_type}: {e}")
        
        logger.info(f"Loaded models for {len(self.models)} prop types")
    
    def predict_single_player_prop(self, player_id: int, game_id: int, 
                                   prop_type: str, is_home: bool) -> Optional[Dict[str, Any]]:
        """
        Generate prediction for a single player and prop type
        
        Args:
            player_id: Player ID
            game_id: Game ID
            prop_type: Type of prop to predict
            is_home: Whether player is at home
            
        Returns:
            Dictionary with prediction details or None
        """
        try:
            # Check if models are loaded
            if prop_type not in self.models:
                logger.warning(f"Models for {prop_type} not loaded")
                return None
            
            # Extract features
            features = self.feature_engineer.extract_features_for_player(
                player_id, game_id, db_manager, is_home, prop_type
            )
            
            if features is None:
                logger.warning(f"Could not extract features for player {player_id}, prop {prop_type}")
                return None
            
            # Convert to DataFrame
            features_df = pd.DataFrame([features])
            
            # Scale features
            scaler = self.scalers[prop_type]
            features_scaled = scaler.transform(features_df)
            
            # Generate predictions from each model
            models = self.models[prop_type]
            predictions = {
                'linear_regression': models['linear_regression'].predict(features_scaled)[0],
                'random_forest': models['random_forest'].predict(features_scaled)[0],
                'gradient_boosting': models['gradient_boosting'].predict(features_scaled)[0]
            }
            
            # Ensemble prediction (average)
            ensemble_pred = np.mean(list(predictions.values()))
            
            # Calculate prediction interval (using std of predictions as proxy)
            pred_std = np.std(list(predictions.values()))
            prediction_low = ensemble_pred - (1.5 * pred_std)
            prediction_high = ensemble_pred + (1.5 * pred_std)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                predictions, features, prop_type
            )
            
            # Get player and game info
            player_info = db_manager.execute_query(
                "SELECT name, position FROM players WHERE id = %s", (player_id,)
            )
            game_info = db_manager.execute_query(
                "SELECT date, home_team_id, away_team_id FROM games WHERE id = %s", (game_id,)
            )
            
            result = {
                'player_id': player_id,
                'player_name': player_info[0]['name'] if player_info else 'Unknown',
                'position': player_info[0]['position'] if player_info else None,
                'game_id': game_id,
                'game_date': str(game_info[0]['date']) if game_info else None,
                'is_home': is_home,
                'prop_type': prop_type,
                'predicted_value': round(ensemble_pred, 2),
                'prediction_low': round(max(0, prediction_low), 2),
                'prediction_high': round(prediction_high, 2),
                'confidence_score': round(confidence, 1),
                'model_predictions': {k: round(v, 2) for k, v in predictions.items()},
                'model_version': MODEL_VERSION,
                'created_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting for player {player_id}, prop {prop_type}: {e}")
            return None
    
    def _calculate_confidence(self, predictions: Dict[str, float], 
                            features: Dict[str, float], 
                            prop_type: str) -> float:
        """
        Calculate confidence score for prediction
        
        Args:
            predictions: Dictionary of model predictions
            features: Feature dictionary
            prop_type: Type of prop
            
        Returns:
            Confidence score (0-100)
        """
        try:
            # 1. Ensemble agreement (how much models agree)
            pred_values = list(predictions.values())
            pred_mean = np.mean(pred_values)
            pred_std = np.std(pred_values)
            
            # Coefficient of variation (lower is better)
            if pred_mean > 0:
                cv = pred_std / pred_mean
                agreement_score = max(0, min(100, 100 - (cv * 200)))
            else:
                agreement_score = 50
            
            # 2. Historical accuracy (from metadata)
            if prop_type in self.metadata:
                ensemble_metrics = self.metadata[prop_type].get('ensemble', {})
                r2 = ensemble_metrics.get('r2', 0.5)
                # Convert R² to confidence (0-1 -> 0-100)
                accuracy_score = max(0, min(100, r2 * 100))
            else:
                accuracy_score = 50
            
            # 3. Data quality (based on games played and consistency)
            games_played = features.get('games_played_this_season', 0)
            consistency = features.get('consistency_score', 50)
            
            if games_played >= 20:
                recency_score = 100
            elif games_played >= 10:
                recency_score = 80
            elif games_played >= 5:
                recency_score = 60
            else:
                recency_score = 40
            
            data_quality_score = (recency_score * 0.6 + consistency * 0.4)
            
            # Weighted combination
            confidence = (
                agreement_score * CONFIDENCE_CONFIG['ensemble_agreement_weight'] +
                accuracy_score * CONFIDENCE_CONFIG['historical_accuracy_weight'] +
                data_quality_score * CONFIDENCE_CONFIG['data_quality_weight']
            )
            
            # Ensure within bounds
            confidence = max(
                CONFIDENCE_CONFIG['min_confidence'],
                min(CONFIDENCE_CONFIG['max_confidence'], confidence)
            )
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 50.0  # Default moderate confidence
    
    def predict_game(self, game_id: int, prop_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate predictions for all players in a game
        
        Args:
            game_id: Game ID
            prop_types: List of prop types to predict (default: all available)
            
        Returns:
            List of prediction dictionaries
        """
        if prop_types is None:
            prop_types = list(self.models.keys())
        
        try:
            # Get game info
            game_info = db_manager.execute_query(
                "SELECT * FROM games WHERE id = %s", (game_id,)
            )
            
            if not game_info:
                logger.error(f"Game {game_id} not found")
                return []
            
            game = game_info[0]
            logger.info(f"Generating predictions for game {game_id} on {game['date']}")
            
            # Get players for both teams
            home_players_query = """
                SELECT p.id, p.name, p.position
                FROM players p
                WHERE p.team_id = %s AND p.is_active = TRUE AND p.sport = 'NBA'
            """
            away_players_query = """
                SELECT p.id, p.name, p.position
                FROM players p
                WHERE p.team_id = %s AND p.is_active = TRUE AND p.sport = 'NBA'
            """
            
            home_players = db_manager.execute_query(home_players_query, (game['home_team_id'],))
            away_players = db_manager.execute_query(away_players_query, (game['away_team_id'],))
            
            logger.info(f"Found {len(home_players)} home players, {len(away_players)} away players")
            
            # Generate predictions
            all_predictions = []
            
            for player in home_players:
                for prop_type in prop_types:
                    pred = self.predict_single_player_prop(
                        player['id'], game_id, prop_type, is_home=True
                    )
                    if pred:
                        all_predictions.append(pred)
            
            for player in away_players:
                for prop_type in prop_types:
                    pred = self.predict_single_player_prop(
                        player['id'], game_id, prop_type, is_home=False
                    )
                    if pred:
                        all_predictions.append(pred)
            
            logger.info(f"Generated {len(all_predictions)} predictions for game {game_id}")
            
            return all_predictions
            
        except Exception as e:
            logger.error(f"Error predicting game {game_id}: {e}")
            return []
    
    def predict_today_games(self, date: str = None, 
                          prop_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate predictions for all games on a specific date
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            prop_types: List of prop types to predict
            
        Returns:
            List of all predictions
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Generating predictions for games on {date}")
        
        try:
            # Get games for the date
            games_query = """
                SELECT id, external_id, date, home_team_id, away_team_id
                FROM games
                WHERE sport = 'NBA' 
                AND date = %s
                AND status IN ('scheduled', 'in_progress')
                ORDER BY time
            """
            
            games = db_manager.execute_query(games_query, (date,))
            
            if not games:
                logger.warning(f"No games found for {date}")
                return []
            
            logger.info(f"Found {len(games)} games on {date}")
            
            # Generate predictions for each game
            all_predictions = []
            
            for game in games:
                game_predictions = self.predict_game(game['id'], prop_types)
                all_predictions.extend(game_predictions)
            
            logger.info(f"Generated {len(all_predictions)} total predictions for {date}")
            
            return all_predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions for {date}: {e}")
            return []
    
    def save_predictions_to_db(self, predictions: List[Dict[str, Any]]) -> int:
        """
        Save predictions to database
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Number of predictions saved
        """
        if not predictions:
            logger.warning("No predictions to save")
            return 0
        
        try:
            logger.info(f"Saving {len(predictions)} predictions to database...")
            
            saved_count = 0
            
            for pred in predictions:
                try:
                    # Check if prediction already exists
                    check_query = """
                        SELECT id FROM projections
                        WHERE player_id = %s 
                        AND game_id = %s 
                        AND prop_type = %s
                        AND DATE(created_at) = CURRENT_DATE
                    """
                    existing = db_manager.execute_query(
                        check_query, 
                        (pred['player_id'], pred['game_id'], pred['prop_type'])
                    )
                    
                    if existing:
                        # Update existing prediction
                        update_query = """
                            UPDATE projections
                            SET projected_value = %s,
                                confidence = %s,
                                model_version = %s,
                                features = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """
                        features_json = json.dumps({
                            'prediction_low': pred['prediction_low'],
                            'prediction_high': pred['prediction_high'],
                            'model_predictions': pred['model_predictions']
                        })
                        db_manager.execute_query(
                            update_query,
                            (pred['predicted_value'], pred['confidence_score'],
                             pred['model_version'], features_json, existing[0]['id']),
                            fetch=False
                        )
                    else:
                        # Insert new prediction
                        insert_query = """
                            INSERT INTO projections 
                            (player_id, game_id, prop_type, projected_value, confidence, model_version, features)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        features_json = json.dumps({
                            'prediction_low': pred['prediction_low'],
                            'prediction_high': pred['prediction_high'],
                            'model_predictions': pred['model_predictions']
                        })
                        db_manager.execute_query(
                            insert_query,
                            (pred['player_id'], pred['game_id'], pred['prop_type'],
                             pred['predicted_value'], pred['confidence_score'],
                             pred['model_version'], features_json),
                            fetch=False
                        )
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving prediction: {e}")
                    continue
            
            logger.info(f"✓ Saved {saved_count} predictions to database")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving predictions to database: {e}")
            return 0


def main():
    """Main function for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate NBA predictions')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--game-id', type=int, help='Specific game ID to predict')
    parser.add_argument('--prop-types', nargs='+', choices=PROP_TYPES,
                       help='Specific prop types to predict')
    parser.add_argument('--save', action='store_true', help='Save predictions to database')
    
    args = parser.parse_args()
    
    try:
        predictor = NBAPredictor()
        
        if args.game_id:
            # Predict specific game
            predictions = predictor.predict_game(args.game_id, args.prop_types)
        else:
            # Predict for date
            predictions = predictor.predict_today_games(args.date, args.prop_types)
        
        if predictions:
            # Print summary
            logger.info(f"\nGenerated {len(predictions)} predictions")
            
            # Group by player
            by_player = {}
            for pred in predictions:
                player_name = pred['player_name']
                if player_name not in by_player:
                    by_player[player_name] = []
                by_player[player_name].append(pred)
            
            # Print sample
            logger.info("\nSample predictions:")
            for i, (player_name, preds) in enumerate(list(by_player.items())[:5]):
                logger.info(f"\n{player_name}:")
                for pred in preds[:3]:  # Show first 3 props
                    logger.info(f"  {pred['prop_type']}: {pred['predicted_value']} "
                              f"(confidence: {pred['confidence_score']})")
            
            # Save if requested
            if args.save:
                saved = predictor.save_predictions_to_db(predictions)
                logger.info(f"\n✓ Saved {saved} predictions to database")
        else:
            logger.warning("No predictions generated")
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
