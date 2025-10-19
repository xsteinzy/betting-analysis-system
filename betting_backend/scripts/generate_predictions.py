
#!/usr/bin/env python3
"""
Unified Predictions Generator for Both NBA and NFL

This script can generate predictions for both sports or run them separately.

Usage:
    python scripts/generate_predictions.py --sport both        # Generate for both sports
    python scripts/generate_predictions.py --sport nba         # NBA only
    python scripts/generate_predictions.py --sport nfl         # NFL only
    python scripts/generate_predictions.py --sport nba --retrain  # Retrain NBA models first
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

# Setup logger
logger = setup_logger('generate_predictions_unified')


def run_nba_predictions(retrain: bool = False, date: str = None, prop_types: list = None) -> int:
    """Run NBA predictions"""
    try:
        logger.info("\n" + "="*60)
        logger.info("GENERATING NBA PREDICTIONS")
        logger.info("="*60 + "\n")
        
        from models.nba.predict import NBAPredictor
        from models.nba.train_models import ModelTrainer
        from models.nba.config import MODELS_DIR as NBA_MODELS_DIR
        
        # Check/train models
        if retrain:
            logger.info("Retraining NBA models...")
            trainer = ModelTrainer()
            trainer.train_all_models()
        else:
            model_files = list(NBA_MODELS_DIR.glob('*.joblib'))
            if not model_files:
                logger.warning("No NBA models found. Training...")
                trainer = ModelTrainer()
                trainer.train_all_models()
        
        # Generate predictions
        predictor = NBAPredictor()
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        predictions = predictor.predict_today_games(date, prop_types)
        
        if predictions:
            saved = predictor.save_predictions_to_db(predictions)
            logger.info(f"✓ NBA: Saved {saved} predictions")
            return saved
        else:
            logger.warning("No NBA predictions generated")
            return 0
            
    except Exception as e:
        logger.error(f"Error running NBA predictions: {e}")
        import traceback
        traceback.print_exc()
        return 0


def run_nfl_predictions(retrain: bool = False, week: int = None, prop_types: list = None) -> int:
    """Run NFL predictions"""
    try:
        logger.info("\n" + "="*60)
        logger.info("GENERATING NFL PREDICTIONS")
        logger.info("="*60 + "\n")
        
        from models.nfl.predict import NFLPredictor
        from models.nfl.train_models import ModelTrainer
        from models.nfl.config import MODELS_DIR as NFL_MODELS_DIR
        
        # Check/train models
        if retrain:
            logger.info("Retraining NFL models...")
            trainer = ModelTrainer()
            trainer.train_all_models()
        else:
            model_files = list(NFL_MODELS_DIR.glob('*.joblib'))
            if not model_files:
                logger.warning("No NFL models found. Training...")
                trainer = ModelTrainer()
                trainer.train_all_models()
        
        # Generate predictions
        predictor = NFLPredictor()
        predictions = predictor.predict_week_games(week)
        
        if predictions:
            saved = predictor.save_predictions_to_db(predictions)
            logger.info(f"✓ NFL: Saved {saved} predictions")
            return saved
        else:
            logger.warning("No NFL predictions generated")
            return 0
            
    except Exception as e:
        logger.error(f"Error running NFL predictions: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate predictions for NBA and/or NFL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate predictions for both sports
  python scripts/generate_predictions.py --sport both
  
  # Generate predictions for NBA only
  python scripts/generate_predictions.py --sport nba
  
  # Generate predictions for NFL only
  python scripts/generate_predictions.py --sport nfl
  
  # Retrain models before generating predictions
  python scripts/generate_predictions.py --sport both --retrain
  
  # NBA specific date
  python scripts/generate_predictions.py --sport nba --date 2024-10-25
  
  # NFL specific week
  python scripts/generate_predictions.py --sport nfl --week 7
        """
    )
    
    parser.add_argument(
        '--sport',
        type=str,
        choices=['nba', 'nfl', 'both'],
        default='both',
        help='Sport to generate predictions for (default: both)'
    )
    
    parser.add_argument(
        '--retrain',
        action='store_true',
        help='Retrain models before generating predictions'
    )
    
    # NBA specific arguments
    parser.add_argument(
        '--date',
        type=str,
        help='NBA: Date to generate predictions for (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--nba-prop-types',
        nargs='+',
        help='NBA: Specific prop types to predict'
    )
    
    # NFL specific arguments
    parser.add_argument(
        '--week',
        type=int,
        help='NFL: Week number to generate predictions for'
    )
    
    parser.add_argument(
        '--nfl-prop-types',
        nargs='+',
        help='NFL: Specific prop types to predict'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info(f"\n{'#'*60}")
        logger.info(f"# UNIFIED PREDICTIONS GENERATOR")
        logger.info(f"# Sport: {args.sport.upper()}")
        logger.info(f"# Retrain: {args.retrain}")
        logger.info(f"# Timestamp: {datetime.now().isoformat()}")
        logger.info(f"{'#'*60}\n")
        
        total_predictions = 0
        
        # Run predictions based on sport selection
        if args.sport in ['nba', 'both']:
            nba_count = run_nba_predictions(
                retrain=args.retrain,
                date=args.date,
                prop_types=args.nba_prop_types
            )
            total_predictions += nba_count
        
        if args.sport in ['nfl', 'both']:
            nfl_count = run_nfl_predictions(
                retrain=args.retrain,
                week=args.week,
                prop_types=args.nfl_prop_types
            )
            total_predictions += nfl_count
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total predictions generated: {total_predictions}")
        
        if total_predictions > 0:
            logger.info("\n✓ SUCCESS!")
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
