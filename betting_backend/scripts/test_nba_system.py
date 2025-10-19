#!/usr/bin/env python3
"""
NBA ML System Test Script

Comprehensive testing of the NBA machine learning prediction system.
Tests all components to ensure they work correctly.

Usage:
    python scripts/test_nba_system.py
    python scripts/test_nba_system.py --verbose
    python scripts/test_nba_system.py --component config
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import logging
import argparse
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    logger.info(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    logger.info(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    logger.info(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    logger.info(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    logger.error(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    logger.warning(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    logger.info(f"  {text}")


def test_imports():
    """Test that all required imports work"""
    print_header("Test 1: Import Dependencies")
    
    tests = []
    
    # Test core Python packages
    try:
        import numpy
        print_success(f"numpy {numpy.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"numpy: {e}")
        tests.append(False)
    
    try:
        import pandas
        print_success(f"pandas {pandas.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"pandas: {e}")
        tests.append(False)
    
    try:
        import sklearn
        print_success(f"scikit-learn {sklearn.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"scikit-learn: {e}")
        tests.append(False)
    
    try:
        import xgboost
        print_success(f"xgboost {xgboost.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"xgboost: {e}")
        tests.append(False)
    
    try:
        import joblib
        print_success(f"joblib {joblib.__version__}")
        tests.append(True)
    except ImportError as e:
        print_error(f"joblib: {e}")
        tests.append(False)
    
    # Test project modules
    try:
        from database.db_manager import db_manager
        print_success("database.db_manager")
        tests.append(True)
    except ImportError as e:
        print_error(f"database.db_manager: {e}")
        tests.append(False)
    
    try:
        from utils.logger import setup_logger
        print_success("utils.logger")
        tests.append(True)
    except ImportError as e:
        print_error(f"utils.logger: {e}")
        tests.append(False)
    
    try:
        from models.nba.config import PROP_TYPES
        print_success("models.nba.config")
        tests.append(True)
    except ImportError as e:
        print_error(f"models.nba.config: {e}")
        tests.append(False)
    
    try:
        from models.nba.feature_engineering import NBAFeatureEngineer
        print_success("models.nba.feature_engineering")
        tests.append(True)
    except ImportError as e:
        print_error(f"models.nba.feature_engineering: {e}")
        tests.append(False)
    
    try:
        from models.nba.train_models import ModelTrainer
        print_success("models.nba.train_models")
        tests.append(True)
    except ImportError as e:
        print_error(f"models.nba.train_models: {e}")
        tests.append(False)
    
    try:
        from models.nba.predict import NBAPredictor
        print_success("models.nba.predict")
        tests.append(True)
    except ImportError as e:
        print_error(f"models.nba.predict: {e}")
        tests.append(False)
    
    try:
        from models.nba.value_finder import ValueFinder
        print_success("models.nba.value_finder")
        tests.append(True)
    except ImportError as e:
        print_error(f"models.nba.value_finder: {e}")
        tests.append(False)
    
    return all(tests)


def test_config():
    """Test NBA configuration"""
    print_header("Test 2: NBA Configuration")
    
    try:
        from models.nba.config import (
            PROP_TYPES, MODEL_PARAMS, TRAINING_CONFIG,
            CONFIDENCE_CONFIG, VALUE_BET_CONFIG, MODELS_DIR
        )
        
        # Test prop types
        print_info("NBA Prop Types:")
        for i, prop in enumerate(PROP_TYPES, 1):
            print_info(f"  {i}. {prop}")
        
        if len(PROP_TYPES) == 10:
            print_success(f"All 10 NBA prop types configured")
        else:
            print_error(f"Expected 10 prop types, found {len(PROP_TYPES)}")
            return False
        
        # Verify NBA-specific props
        nba_props = ['points', 'rebounds', 'assists', 'three_pt_made', 'steals', 
                     'blocks', 'turnovers', 'double_double', 'fg_made', 'ft_made']
        
        for prop in nba_props:
            if prop in PROP_TYPES:
                print_success(f"NBA-specific prop '{prop}' found")
            else:
                print_error(f"Missing NBA prop '{prop}'")
                return False
        
        # Test model parameters
        print_info("\nModel Configurations:")
        for model_name in MODEL_PARAMS:
            print_success(f"{model_name}: {len(MODEL_PARAMS[model_name])} parameters")
        
        # Test training config
        print_info("\nTraining Configuration:")
        for key, value in TRAINING_CONFIG.items():
            print_info(f"  {key}: {value}")
        
        # Test models directory exists
        if MODELS_DIR.exists():
            print_success(f"Models directory exists: {MODELS_DIR}")
        else:
            print_warning(f"Models directory doesn't exist yet: {MODELS_DIR}")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_engineering():
    """Test NBA feature engineering"""
    print_header("Test 3: Feature Engineering")
    
    try:
        from models.nba.feature_engineering import NBAFeatureEngineer
        
        fe = NBAFeatureEngineer()
        print_success("NBAFeatureEngineer instantiated")
        
        # Test double-double calculation
        print_info("\nTesting double-double calculation:")
        
        test_cases = [
            ({'points': 15, 'rebounds': 12, 'assists': 5}, 1, "points + rebounds"),
            ({'points': 15, 'rebounds': 8, 'assists': 5}, 0, "no double-double"),
            ({'points': 8, 'rebounds': 10, 'assists': 11}, 1, "rebounds + assists"),
            ({'points': 12, 'rebounds': 10, 'assists': 5}, 1, "points + rebounds"),
            ({'points': 25, 'rebounds': 15, 'assists': 11}, 1, "triple-double"),
        ]
        
        for stats, expected, description in test_cases:
            result = fe.calculate_double_double(stats)
            if result == expected:
                print_success(f"{description}: {stats} → {result} ✓")
            else:
                print_error(f"{description}: {stats} → {result} (expected {expected})")
                return False
        
        print_success("All double-double tests passed")
        
        # Test that feature engineer has required methods
        required_methods = [
            'calculate_double_double',
            'extract_features_for_player',
            'prepare_training_data'
        ]
        
        for method in required_methods:
            if hasattr(fe, method):
                print_success(f"Method '{method}' exists")
            else:
                print_error(f"Missing method '{method}'")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Feature engineering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test database connection and schema"""
    print_header("Test 4: Database Connection")
    
    try:
        from database.db_manager import db_manager
        
        # Test connection
        result = db_manager.execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            print_success("Database connection successful")
        else:
            print_error("Database connection failed")
            return False
        
        # Check required tables exist
        tables = ['teams', 'players', 'games', 'player_game_stats', 'projections', 'bets']
        
        for table in tables:
            result = db_manager.execute_query(
                f"SELECT COUNT(*) as count FROM {table}"
            )
            if result is not None:
                count = result[0]['count']
                print_success(f"Table '{table}': {count} rows")
            else:
                print_error(f"Table '{table}' not found")
                return False
        
        # Check NBA-specific data
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM teams WHERE sport = 'NBA'"
        )
        nba_teams = result[0]['count']
        print_info(f"\nNBA Teams: {nba_teams}")
        
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM players WHERE sport = 'NBA'"
        )
        nba_players = result[0]['count']
        print_info(f"NBA Players: {nba_players}")
        
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM games WHERE sport = 'NBA'"
        )
        nba_games = result[0]['count']
        print_info(f"NBA Games: {nba_games}")
        
        result = db_manager.execute_query("""
            SELECT COUNT(*) as count 
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.id
            WHERE g.sport = 'NBA'
        """)
        nba_stats = result[0]['count']
        print_info(f"NBA Player Game Stats: {nba_stats}")
        
        if nba_stats < 100:
            print_warning("Consider collecting more NBA data for better model training (need 500+)")
        else:
            print_success(f"Sufficient NBA data available for training")
        
        db_manager.close()
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models_exist():
    """Test if trained models exist"""
    print_header("Test 5: Trained Models")
    
    try:
        from models.nba.config import MODELS_DIR, PROP_TYPES
        
        if not MODELS_DIR.exists():
            print_warning("Models directory doesn't exist")
            print_info("Run 'python models/nba/train_models.py' to train models")
            return False
        
        print_info(f"Models directory: {MODELS_DIR}")
        
        model_files = list(MODELS_DIR.glob('*.joblib'))
        
        if not model_files:
            print_warning("No trained models found")
            print_info("Run 'python models/nba/train_models.py' to train models")
            return False
        
        print_success(f"Found {len(model_files)} model files")
        
        # Check each prop type
        for prop_type in PROP_TYPES:
            expected_files = [
                f'{prop_type}_linear_regression.joblib',
                f'{prop_type}_random_forest.joblib',
                f'{prop_type}_gradient_boosting.joblib',
                f'{prop_type}_scaler.joblib',
                f'{prop_type}_metadata.json'
            ]
            
            all_exist = True
            for filename in expected_files:
                filepath = MODELS_DIR / filename
                if filepath.exists():
                    continue
                else:
                    all_exist = False
                    break
            
            if all_exist:
                print_success(f"Models for '{prop_type}' are complete")
            else:
                print_warning(f"Models for '{prop_type}' are incomplete or missing")
        
        return True
        
    except Exception as e:
        print_error(f"Model check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_predictor():
    """Test NBA predictor can be instantiated"""
    print_header("Test 6: NBA Predictor")
    
    try:
        from models.nba.predict import NBAPredictor
        
        predictor = NBAPredictor()
        print_success("NBAPredictor instantiated successfully")
        
        # Check how many models were loaded
        loaded_props = len(predictor.models)
        print_info(f"Loaded models for {loaded_props} prop types")
        
        if loaded_props == 0:
            print_warning("No models loaded. Train models first with:")
            print_info("  python models/nba/train_models.py")
            return False
        
        if loaded_props < 10:
            print_warning(f"Only {loaded_props}/10 models loaded")
        else:
            print_success(f"All 10 models loaded successfully")
        
        # Test required methods exist
        required_methods = [
            'predict_single_player_prop',
            'predict_today_games',
            'save_predictions_to_db'
        ]
        
        for method in required_methods:
            if hasattr(predictor, method):
                print_success(f"Method '{method}' exists")
            else:
                print_error(f"Missing method '{method}'")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Predictor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_value_finder():
    """Test value finder"""
    print_header("Test 7: Value Finder")
    
    try:
        from models.nba.value_finder import ValueFinder
        
        vf = ValueFinder()
        print_success("ValueFinder instantiated successfully")
        
        # Test expected value calculation
        print_info("\nTesting EV calculation:")
        
        ev_result = vf.calculate_expected_value(
            predicted_value=28.5,
            betting_line=25.5,
            confidence=75,
            odds=-110
        )
        
        print_info(f"Prediction: 28.5 vs Line: 25.5")
        print_info(f"Edge: {ev_result['edge']}")
        print_info(f"Win Probability: {ev_result['win_probability']}%")
        print_info(f"Expected Value: {ev_result['ev_pct']}%")
        
        if ev_result['edge'] > 0:
            print_success("EV calculation working correctly (positive edge)")
        else:
            print_error("EV calculation may have issues")
            return False
        
        # Test required methods
        required_methods = [
            'calculate_expected_value',
            'evaluate_bet',
            'find_best_values'
        ]
        
        for method in required_methods:
            if hasattr(vf, method):
                print_success(f"Method '{method}' exists")
            else:
                print_error(f"Missing method '{method}'")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Value finder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scripts_exist():
    """Test that required scripts exist"""
    print_header("Test 8: Required Scripts")
    
    try:
        scripts = [
            'scripts/generate_nba_predictions.py',
            'models/nba/train_models.py',
            'models/nba/predict.py',
            'models/nba/value_finder.py',
            'models/nba/feature_engineering.py',
            'models/nba/config.py',
            'models/nba/README.md'
        ]
        
        base_dir = Path(__file__).parent.parent
        
        for script in scripts:
            script_path = base_dir / script
            if script_path.exists():
                print_success(f"{script}")
            else:
                print_error(f"{script} not found")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Script check failed: {e}")
        return False


def run_all_tests(verbose=False):
    """Run all tests"""
    print_header("NBA Machine Learning System - Comprehensive Test Suite")
    
    tests = [
        ("Import Dependencies", test_imports),
        ("NBA Configuration", test_config),
        ("Feature Engineering", test_feature_engineering),
        ("Database Connection", test_database),
        ("Trained Models", test_models_exist),
        ("NBA Predictor", test_predictor),
        ("Value Finder", test_value_finder),
        ("Required Scripts", test_scripts_exist)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        print(f"\n{Colors.GREEN}NBA ML System is ready to use!{Colors.END}")
        print(f"\nNext steps:")
        print(f"  1. Ensure you have sufficient data (500+ player game stats)")
        print(f"  2. Train models: python models/nba/train_models.py")
        print(f"  3. Generate predictions: python scripts/generate_nba_predictions.py")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"\nPlease fix the issues above before using the NBA ML system.")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Test NBA Machine Learning System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--component', '-c',
        choices=['imports', 'config', 'features', 'database', 'models', 
                'predictor', 'value', 'scripts', 'all'],
        default='all',
        help='Test specific component'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    component_map = {
        'imports': test_imports,
        'config': test_config,
        'features': test_feature_engineering,
        'database': test_database,
        'models': test_models_exist,
        'predictor': test_predictor,
        'value': test_value_finder,
        'scripts': test_scripts_exist,
        'all': run_all_tests
    }
    
    if args.component == 'all':
        success = run_all_tests(args.verbose)
    else:
        print_header(f"Testing: {args.component}")
        success = component_map[args.component]()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
