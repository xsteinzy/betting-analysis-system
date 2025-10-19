#!/usr/bin/env python3
"""
Daily NBA Predictions Generator

This script generates predictions for today's NBA games and saves them to the database.
Can be run manually or scheduled via cron job.

Usage:
    python scripts/generate_nba_predictions.py                    # Predict today's games
    python scripts/generate_nba_predictions.py --date 2024-10-25  # Predict specific date
    python scripts/generate_nba_predictions.py --retrain          # Retrain models first
"""
import logging
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager
from utils.logger import setup_logger
from models.nba.config import PROP_TYPES
from models.nba.predict import NBAPredictor
from models.nba.train_models import ModelTrainer

# Setup logger
logger = setup_logger('generate_predictions')


def check_models_exist() -> bool:
    """Check if trained models exist"""
    from models.nba.config import MODELS_DIR
    
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


def check_data_availability(date: str) -> bool:
    """
    Check if we have sufficient data to make predictions
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        True if data is available
    """
    try:
        # Check if games exist for the date
        games_query = """
            SELECT COUNT(*) as count
            FROM games
            WHERE sport = 'NBA' 
            AND date = %s
        """
        result = db_manager.execute_query(games_query, (date,))
        
        if not result or result[0]['count'] == 0:
            logger.warning(f"No games found for {date}")
            return False
        
        logger.info(f"Found {result[0]['count']} game(s) for {date}")
        
        # Check if we have player stats
        stats_query = """
            SELECT COUNT(*) as count
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.id
            WHERE g.sport = 'NBA' 
            AND g.status = 'completed'
        """
        result = db_manager.execute_query(stats_query)
        
        if not result or result[0]['count'] < 100:
            logger.warning(f"Insufficient historical data: only {result[0]['count']} player game stats")
            return False
        
        logger.info(f"Found {result[0]['count']} historical player game stats")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking data availability: {e}")
        return False


def generate_predictions(date: str, prop_types: list = None) -> int:
    """
    Generate predictions for a specific date
    
    Args:
        date: Date in YYYY-MM-DD format
        prop_types: List of prop types to predict (default: all)
        
    Returns:
        Number of predictions generated
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Generating NBA Predictions for {date}")
        logger.info(f"{'='*60}\n")
        
        # Create predictor
        predictor = NBAPredictor()
        
        # Generate predictions
        predictions = predictor.predict_today_games(date, prop_types)
        
        if not predictions:
            logger.warning(f"No predictions generated for {date}")
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
        
        # Show high confidence predictions
        high_conf = [p for p in predictions if p['confidence_score'] >= 75]
        if high_conf:
            logger.info(f"\nHigh Confidence Predictions (>75%):")
            for pred in high_conf[:10]:  # Show top 10
                logger.info(
                    f"  {pred['player_name']}: {pred['prop_type']} = {pred['predicted_value']} "
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
        description='Generate NBA predictions for daily games',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict today's games
  python scripts/generate_nba_predictions.py
  
  # Predict specific date
  python scripts/generate_nba_predictions.py --date 2024-10-25
  
  # Retrain models first, then predict
  python scripts/generate_nba_predictions.py --retrain
  
  # Predict only specific prop types
  python scripts/generate_nba_predictions.py --prop-types points rebounds assists
  
  # Check if data is ready without generating predictions
  python scripts/generate_nba_predictions.py --check-only
        """
    )
    
    parser.add_argument(
        '--date',
        type=str,
        help='Date to generate predictions for (YYYY-MM-DD). Default: today'
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
    
    parser.add_argument(
        '--days-ahead',
        type=int,
        default=0,
        help='Generate predictions for N days ahead (0 = today, 1 = tomorrow, etc.)'
    )
    
    args = parser.parse_args()
    
    try:
        # Determine date
        if args.date:
            prediction_date = args.date
        else:
            date_obj = datetime.now() + timedelta(days=args.days_ahead)
            prediction_date = date_obj.strftime('%Y-%m-%d')
        
        logger.info(f"Target date: {prediction_date}")
        
        # Check data availability
        logger.info("\nChecking data availability...")
        if not check_data_availability(prediction_date):
            logger.error("Insufficient data to generate predictions")
            logger.info("\nPlease run data collection first:")
            logger.info("  python collect_data.py --with-stats")
            sys.exit(1)
        
        if args.check_only:
            logger.info("✓ Data check passed. Ready to generate predictions.")
            sys.exit(0)
        
        # Train or check models
        logger.info("\nChecking models...")
        if not train_models_if_needed(args.retrain):
            logger.error("Models not ready")
            logger.info("\nPlease train models first:")
            logger.info("  python models/nba/train_models.py")
            sys.exit(1)
        
        logger.info("✓ Models ready")
        
        # Generate predictions
        predictions_count = generate_predictions(prediction_date, args.prop_types)
        
        if predictions_count > 0:
            logger.info(f"\n{'='*60}")
            logger.info("SUCCESS!")
            logger.info(f"{'='*60}")
            logger.info(f"Generated and saved {predictions_count} predictions for {prediction_date}")
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
