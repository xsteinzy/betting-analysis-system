
#!/usr/bin/env python3
"""
Weekly NFL Predictions Generator

This script generates predictions for this week's NFL games and saves them to the database.
Can be run manually or scheduled via cron job.

Usage:
    python scripts/generate_nfl_predictions.py                    # Predict current week's games
    python scripts/generate_nfl_predictions.py --week 7           # Predict specific week
    python scripts/generate_nfl_predictions.py --retrain          # Retrain models first
"""
import logging
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager
from utils.logger import setup_logger
from models.nfl.config import PROP_TYPES
from models.nfl.predict import NFLPredictor
from models.nfl.train_models import ModelTrainer

# Setup logger
logger = setup_logger('generate_predictions_nfl')


def check_models_exist() -> bool:
    """Check if trained models exist"""
    from models.nfl.config import MODELS_DIR
    
    # Check if at least one model exists
    model_files = list(MODELS_DIR.glob('*.joblib'))
    
    if not model_files:
        logger.warning("No trained models found!")
        return False
    
    logger.info(f"Found {len(model_files)} model files")
    return True


def train_models_if_needed(force_retrain: bool = False) -> bool:
    """
    Train models if they don't exist or if force_retrain is True
    
    Args:
        force_retrain: Force retraining even if models exist
        
    Returns:
        True if models are ready, False otherwise
    """
    if force_retrain:
        logger.info("Force retraining models...")
        trainer = ModelTrainer()
        results = trainer.train_all_models()
        return len(results) > 0
    
    if not check_models_exist():
        logger.info("No models found. Training models...")
        trainer = ModelTrainer()
        results = trainer.train_all_models()
        return len(results) > 0
    
    return True


def check_data_availability(week: int = None) -> bool:
    """
    Check if we have sufficient data to make predictions
    
    Args:
        week: Week number (None for current week)
        
    Returns:
        True if data is available
    """
    try:
        # Check if games exist for the week
        if week:
            games_query = """
                SELECT COUNT(*) as count
                FROM games
                WHERE sport = 'NFL' 
                AND week = %s
            """
            result = db_manager.execute_query(games_query, (week,))
        else:
            games_query = """
                SELECT COUNT(*) as count
                FROM games
                WHERE sport = 'NFL' 
                AND date >= CURRENT_DATE
                AND status IN ('scheduled', 'in_progress')
            """
            result = db_manager.execute_query(games_query)
        
        if not result or result[0]['count'] == 0:
            logger.warning(f"No games found for week {week if week else 'current'}")
            return False
        
        logger.info(f"Found {result[0]['count']} game(s) for week {week if week else 'current'}")
        
        # Check if we have player stats
        stats_query = """
            SELECT COUNT(*) as count
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.id
            WHERE g.sport = 'NFL' 
            AND g.status = 'completed'
        """
        result = db_manager.execute_query(stats_query)
        
        if not result or result[0]['count'] < 50:
            logger.warning(f"Insufficient historical data: only {result[0]['count']} player game stats")
            return False
        
        logger.info(f"Found {result[0]['count']} historical player game stats")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking data availability: {e}")
        return False


def generate_predictions(week: int = None, prop_types: list = None) -> int:
    """
    Generate predictions for a specific week
    
    Args:
        week: Week number (None for current week)
        prop_types: List of prop types to predict (default: all)
        
    Returns:
        Number of predictions generated
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Generating NFL Predictions for Week {week if week else 'Current'}")
        logger.info(f"{'='*60}\n")
        
        # Create predictor
        predictor = NFLPredictor()
        
        # Generate predictions
        predictions = predictor.predict_week_games(week)
        
        if not predictions:
            logger.warning(f"No predictions generated for week {week if week else 'current'}")
            return 0
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Prediction Summary")
        logger.info(f"{'='*60}")
        logger.info(f"Total predictions: {len(predictions)}")
        
        # Group by prop type
        by_prop = {}
        for pred in predictions:
            prop_type = pred['prop_type']
            if prop_type not in by_prop:
                by_prop[prop_type] = []
            by_prop[prop_type].append(pred)
        
        logger.info(f"\nBy Prop Type:")
        for prop_type, preds in sorted(by_prop.items()):
            avg_conf = sum(p['confidence_score'] for p in preds) / len(preds)
            logger.info(f"  {prop_type}: {len(preds)} predictions (avg confidence: {avg_conf:.1f}%)")
        
        # Group by position
        by_position = {}
        for pred in predictions:
            position = pred.get('position', 'Unknown')
            if position not in by_position:
                by_position[position] = []
            by_position[position].append(pred)
        
        logger.info(f"\nBy Position:")
        for position, preds in sorted(by_position.items()):
            logger.info(f"  {position}: {len(preds)} predictions")
        
        # Show high confidence predictions
        high_conf = [p for p in predictions if p['confidence_score'] >= 75]
        if high_conf:
            logger.info(f"\nHigh Confidence Predictions (>75%):")
            for pred in high_conf[:10]:  # Show top 10
                logger.info(
                    f"  {pred['player_name']} ({pred.get('position', '')}): {pred['prop_type']} = {pred['predicted_value']} "
                    f"(confidence: {pred['confidence_score']}%)"
                )
        
        # Save to database
        saved = predictor.save_predictions_to_db(predictions)
        
        logger.info(f"\n✓ Successfully saved {saved} predictions to database")
        
        return saved
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate NFL predictions for weekly games',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict current week's games
  python scripts/generate_nfl_predictions.py
  
  # Predict specific week
  python scripts/generate_nfl_predictions.py --week 7
  
  # Retrain models first, then predict
  python scripts/generate_nfl_predictions.py --retrain
  
  # Predict only specific prop types
  python scripts/generate_nfl_predictions.py --prop-types passing_yards rushing_yards
  
  # Check if data is ready without generating predictions
  python scripts/generate_nfl_predictions.py --check-only
        """
    )
    
    parser.add_argument(
        '--week',
        type=int,
        help='Week number to generate predictions for. Default: current week'
    )
    
    parser.add_argument(
        '--retrain',
        action='store_true',
        help='Retrain models before generating predictions'
    )
    
    parser.add_argument(
        '--prop-types',
        nargs='+',
        choices=PROP_TYPES,
        help='Specific prop types to predict (default: all)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check data availability, do not generate predictions'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Target week: {args.week if args.week else 'Current'}")
        
        # Check data availability
        logger.info("\nChecking data availability...")
        if not check_data_availability(args.week):
            logger.error("Insufficient data to generate predictions")
            logger.info("\nPlease run data collection first:")
            logger.info("  python collect_data.py --sport NFL")
            sys.exit(1)
        
        if args.check_only:
            logger.info("✓ Data check passed. Ready to generate predictions.")
            sys.exit(0)
        
        # Train or check models
        logger.info("\nChecking models...")
        if not train_models_if_needed(args.retrain):
            logger.error("Models not ready")
            logger.info("\nPlease train models first:")
            logger.info("  python models/nfl/train_models.py")
            sys.exit(1)
        
        logger.info("✓ Models ready")
        
        # Generate predictions
        predictions_count = generate_predictions(args.week, args.prop_types)
        
        if predictions_count > 0:
            logger.info(f"\n{'='*60}")
            logger.info("SUCCESS!")
            logger.info(f"{'='*60}")
            logger.info(f"Generated and saved {predictions_count} predictions for week {args.week if args.week else 'current'}")
            logger.info("\nYou can now:")
            logger.info("  1. View predictions in the dashboard")
            logger.info("  2. Compare to betting lines using value finder")
            logger.info("  3. Check the projections table in the database")
            sys.exit(0)
        else:
            logger.error("Failed to generate predictions")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
