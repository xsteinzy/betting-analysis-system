"""
NFL ML Model Training Pipeline
Train models for all prop types and save to disk
"""
import logging
import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import project modules
from database.db_manager import db_manager
from utils.logger import setup_logger
from models.nfl.config import (
    PROP_TYPES, MODEL_PARAMS, TRAINING_CONFIG, 
    MODEL_FILES, MODEL_VERSION, MODELS_DIR
)
from models.nfl.feature_engineering import NFLFeatureEngineer

# Setup logger
logger = setup_logger('train_models_nfl')


class ModelTrainer:
    """Train and evaluate NFL prediction models"""
    
    def __init__(self):
        self.feature_engineer = NFLFeatureEngineer()
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
    
    def train_model_for_prop(self, prop_type: str) -> Optional[Dict[str, Any]]:
        """
        Train models for a specific prop type
        
        Args:
            prop_type: Type of prop to predict (e.g., 'passing_yards', 'rushing_yards')
            
        Returns:
            Dictionary with training results and metrics
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Training models for {prop_type}")
            logger.info(f"{'='*60}")
            
            # Prepare training data
            training_data = self.feature_engineer.prepare_training_data(
                db_manager, 
                prop_type, 
                min_games=TRAINING_CONFIG['min_games_required']
            )
            
            if training_data is None:
                logger.error(f"Failed to prepare training data for {prop_type}")
                return None
            
            X, y, game_ids, player_ids = training_data
            
            logger.info(f"Training set size: {len(X)} examples")
            logger.info(f"Number of features: {X.shape[1]}")
            logger.info(f"Target statistics - Mean: {y.mean():.2f}, Std: {y.std():.2f}")
            
            # Split data (time-based split to prevent data leakage)
            # Since data is already sorted by date descending, we take the last 20% for testing
            test_size = int(len(X) * TRAINING_CONFIG['test_size'])
            train_size = len(X) - test_size
            
            X_train = X.iloc[:train_size]
            X_test = X.iloc[train_size:]
            y_train = y[:train_size]
            y_test = y[train_size:]
            
            logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train multiple models
            models = {}
            predictions = {}
            
            # 1. Linear Regression
            logger.info("\nTraining Linear Regression...")
            lr = LinearRegression(**MODEL_PARAMS['linear_regression'])
            lr.fit(X_train_scaled, y_train)
            models['linear_regression'] = lr
            predictions['linear_regression'] = lr.predict(X_test_scaled)
            
            # 2. Random Forest
            logger.info("Training Random Forest...")
            rf = RandomForestRegressor(**MODEL_PARAMS['random_forest'])
            rf.fit(X_train_scaled, y_train)
            models['random_forest'] = rf
            predictions['random_forest'] = rf.predict(X_test_scaled)
            
            # 3. Gradient Boosting
            logger.info("Training Gradient Boosting...")
            gb = GradientBoostingRegressor(**MODEL_PARAMS['gradient_boosting'])
            gb.fit(X_train_scaled, y_train)
            models['gradient_boosting'] = gb
            predictions['gradient_boosting'] = gb.predict(X_test_scaled)
            
            # Ensemble prediction (average of all models)
            ensemble_predictions = np.mean([
                predictions['linear_regression'],
                predictions['random_forest'],
                predictions['gradient_boosting']
            ], axis=0)
            
            # Evaluate models
            logger.info(f"\n{'='*60}")
            logger.info(f"Model Performance on Test Set ({prop_type})")
            logger.info(f"{'='*60}")
            
            results = {
                'prop_type': prop_type,
                'training_date': datetime.now().isoformat(),
                'model_version': MODEL_VERSION,
                'train_size': len(X_train),
                'test_size': len(X_test),
                'n_features': X_train.shape[1],
                'feature_names': list(X.columns),
                'models': {}
            }
            
            # Determine appropriate accuracy thresholds based on prop type
            # NFL has larger values for yards, smaller for TDs
            if 'yards' in prop_type:
                thresholds = [10, 20, 30]  # yards
            elif 'touchdowns' in prop_type or 'interceptions' in prop_type or 'field_goals' in prop_type:
                thresholds = [1, 2, 3]  # TDs/INTs/FGs
            elif 'completions' in prop_type or 'receptions' in prop_type:
                thresholds = [2, 3, 5]  # Completions/Receptions
            else:
                thresholds = [5, 10, 15]  # Default
            
            # Evaluate each model
            for model_name, preds in predictions.items():
                mae = mean_absolute_error(y_test, preds)
                rmse = np.sqrt(mean_squared_error(y_test, preds))
                r2 = r2_score(y_test, preds)
                
                # Calculate accuracy within thresholds
                within_threshold_1 = np.mean(np.abs(y_test - preds) <= thresholds[0]) * 100
                within_threshold_2 = np.mean(np.abs(y_test - preds) <= thresholds[1]) * 100
                within_threshold_3 = np.mean(np.abs(y_test - preds) <= thresholds[2]) * 100
                
                results['models'][model_name] = {
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'r2': float(r2),
                    f'within_{thresholds[0]}': float(within_threshold_1),
                    f'within_{thresholds[1]}': float(within_threshold_2),
                    f'within_{thresholds[2]}': float(within_threshold_3)
                }
                
                logger.info(f"\n{model_name.upper()}:")
                logger.info(f"  MAE: {mae:.3f}")
                logger.info(f"  RMSE: {rmse:.3f}")
                logger.info(f"  R²: {r2:.3f}")
                logger.info(f"  Within {thresholds[0]}: {within_threshold_1:.1f}%")
                logger.info(f"  Within {thresholds[1]}: {within_threshold_2:.1f}%")
                logger.info(f"  Within {thresholds[2]}: {within_threshold_3:.1f}%")
            
            # Evaluate ensemble
            mae_ensemble = mean_absolute_error(y_test, ensemble_predictions)
            rmse_ensemble = np.sqrt(mean_squared_error(y_test, ensemble_predictions))
            r2_ensemble = r2_score(y_test, ensemble_predictions)
            
            within_threshold_1_ensemble = np.mean(np.abs(y_test - ensemble_predictions) <= thresholds[0]) * 100
            within_threshold_2_ensemble = np.mean(np.abs(y_test - ensemble_predictions) <= thresholds[1]) * 100
            within_threshold_3_ensemble = np.mean(np.abs(y_test - ensemble_predictions) <= thresholds[2]) * 100
            
            results['ensemble'] = {
                'mae': float(mae_ensemble),
                'rmse': float(rmse_ensemble),
                'r2': float(r2_ensemble),
                f'within_{thresholds[0]}': float(within_threshold_1_ensemble),
                f'within_{thresholds[1]}': float(within_threshold_2_ensemble),
                f'within_{thresholds[2]}': float(within_threshold_3_ensemble)
            }
            
            logger.info(f"\nENSEMBLE (Average of all models):")
            logger.info(f"  MAE: {mae_ensemble:.3f}")
            logger.info(f"  RMSE: {rmse_ensemble:.3f}")
            logger.info(f"  R²: {r2_ensemble:.3f}")
            logger.info(f"  Within {thresholds[0]}: {within_threshold_1_ensemble:.1f}%")
            logger.info(f"  Within {thresholds[1]}: {within_threshold_2_ensemble:.1f}%")
            logger.info(f"  Within {thresholds[2]}: {within_threshold_3_ensemble:.1f}%")
            
            # Feature importance (from Random Forest)
            feature_importance = dict(zip(X.columns, rf.feature_importances_))
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            logger.info(f"\nTop 10 Feature Importances (Random Forest):")
            for i, (feature, importance) in enumerate(sorted_features[:10], 1):
                logger.info(f"  {i}. {feature}: {importance:.4f}")
            
            results['feature_importance'] = {k: float(v) for k, v in feature_importance.items()}
            
            # Cross-validation on training set
            logger.info(f"\nPerforming {TRAINING_CONFIG['cv_folds']}-Fold Cross-Validation on training set...")
            kfold = KFold(n_splits=TRAINING_CONFIG['cv_folds'], shuffle=False)
            
            cv_scores = {}
            for model_name, model in models.items():
                scores = cross_val_score(model, X_train_scaled, y_train, 
                                       cv=kfold, 
                                       scoring='neg_mean_absolute_error',
                                       n_jobs=-1)
                cv_mae = -scores.mean()
                cv_std = scores.std()
                cv_scores[model_name] = {'mae': float(cv_mae), 'std': float(cv_std)}
                logger.info(f"  {model_name}: MAE = {cv_mae:.3f} (+/- {cv_std:.3f})")
            
            results['cross_validation'] = cv_scores
            
            # Save models
            logger.info(f"\nSaving models for {prop_type}...")
            model_files = MODEL_FILES[prop_type]
            
            joblib.dump(models['linear_regression'], model_files['linear_regression'])
            joblib.dump(models['random_forest'], model_files['random_forest'])
            joblib.dump(models['gradient_boosting'], model_files['gradient_boosting'])
            joblib.dump(scaler, model_files['scaler'])
            
            # Save metadata
            with open(model_files['metadata'], 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Models saved to {MODELS_DIR}")
            logger.info(f"Training complete for {prop_type}!")
            
            return results
            
        except Exception as e:
            logger.error(f"Error training models for {prop_type}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def train_all_models(self, prop_types: List[str] = None) -> Dict[str, Any]:
        """
        Train models for all prop types
        
        Args:
            prop_types: List of prop types to train (default: all)
            
        Returns:
            Dictionary with results for all prop types
        """
        if prop_types is None:
            prop_types = PROP_TYPES
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"Starting NFL ML Model Training Pipeline")
        logger.info(f"Model Version: {MODEL_VERSION}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Prop Types: {', '.join(prop_types)}")
        logger.info(f"{'#'*60}\n")
        
        all_results = {}
        successful = 0
        failed = 0
        
        for prop_type in prop_types:
            result = self.train_model_for_prop(prop_type)
            if result is not None:
                all_results[prop_type] = result
                successful += 1
            else:
                failed += 1
        
        # Generate summary report
        logger.info(f"\n{'#'*60}")
        logger.info(f"Training Pipeline Complete!")
        logger.info(f"{'#'*60}")
        logger.info(f"Successfully trained: {successful} prop types")
        logger.info(f"Failed: {failed} prop types")
        
        if all_results:
            logger.info(f"\nSummary of Model Performance (Test Set MAE):")
            logger.info(f"{'Prop Type':<25} {'Ensemble MAE':<15} {'Best Model':<20}")
            logger.info(f"{'-'*60}")
            
            for prop_type, result in all_results.items():
                ensemble_mae = result['ensemble']['mae']
                best_model = min(result['models'].items(), key=lambda x: x[1]['mae'])
                best_model_name = best_model[0]
                logger.info(f"{prop_type:<25} {ensemble_mae:<15.3f} {best_model_name:<20}")
        
        # Save summary report
        summary_file = MODELS_DIR / f'training_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'model_version': MODEL_VERSION,
                'successful': successful,
                'failed': failed,
                'results': all_results
            }, f, indent=2)
        
        logger.info(f"\nSummary report saved to {summary_file}")
        
        return all_results


def main():
    """Main function to run training"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train NFL ML prediction models')
    parser.add_argument('--prop-types', nargs='+', choices=PROP_TYPES,
                       help='Specific prop types to train (default: all)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: train only one prop type (passing_yards)')
    
    args = parser.parse_args()
    
    try:
        trainer = ModelTrainer()
        
        if args.test:
            logger.info("Running in TEST mode - training passing_yards only")
            prop_types = ['passing_yards']
        elif args.prop_types:
            prop_types = args.prop_types
        else:
            prop_types = PROP_TYPES
        
        results = trainer.train_all_models(prop_types)
        
        logger.info("\n✓ Training pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
