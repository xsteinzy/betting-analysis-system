
#!/usr/bin/env python3
"""
Test NBA ML Prediction System

Comprehensive test script to verify the entire system is working correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager
from models.nba.config import PROP_TYPES, MODELS_DIR
from models.nba.predict import NBAPredictor
from models.nba.value_finder import ValueFinder
from models.nba.train_models import ModelTrainer
from models.nba.feature_engineering import NBAFeatureEngineer


class SystemTester:
    """Test the NBA ML prediction system"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def run_test(self, test_name, test_func):
        """Run a single test"""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            if result:
                print(f"✓ PASS")
                self.tests_passed += 1
                self.results.append((test_name, "PASS", None))
            else:
                print(f"✗ FAIL")
                self.tests_failed += 1
                self.results.append((test_name, "FAIL", "Test returned False"))
        except Exception as e:
            print(f"✗ FAIL: {e}")
            self.tests_failed += 1
            self.results.append((test_name, "FAIL", str(e)))
    
    def test_1_database_connection(self):
        """Test database connection"""
        result = db_manager.execute_query("SELECT 1")
        return result is not None
    
    def test_2_data_availability(self):
        """Test if sufficient data exists"""
        # Check for games
        games = db_manager.execute_query("""
            SELECT COUNT(*) as count FROM games WHERE sport = 'NBA'
        """)
        
        if not games or games[0]['count'] == 0:
            print("No NBA games in database")
            return False
        
        print(f"Found {games[0]['count']} NBA games")
        
        # Check for player stats
        stats = db_manager.execute_query("""
            SELECT COUNT(*) as count FROM player_game_stats
        """)
        
        if not stats or stats[0]['count'] < 100:
            print(f"Insufficient player stats: {stats[0]['count'] if stats else 0}")
            return False
        
        print(f"Found {stats[0]['count']} player game stats")
        return True
    
    def test_3_feature_engineering(self):
        """Test feature engineering"""
        engineer = NBAFeatureEngineer()
        
        # Get a player with stats
        player_stats = db_manager.execute_query("""
            SELECT DISTINCT player_id, game_id, is_home
            FROM player_game_stats
            LIMIT 1
        """)
        
        if not player_stats:
            print("No player stats to test with")
            return False
        
        player = player_stats[0]
        
        # Try to extract features
        features = engineer.extract_features_for_player(
            player['player_id'],
            player['game_id'],
            db_manager,
            player['is_home'],
            'points'
        )
        
        if features is None:
            print("Could not extract features")
            return False
        
        print(f"Extracted {len(features)} features")
        print(f"Sample features: {list(features.keys())[:5]}")
        return True
    
    def test_4_models_exist(self):
        """Test if trained models exist"""
        model_files = list(MODELS_DIR.glob('*.joblib'))
        
        if not model_files:
            print("No trained models found")
            print("Please run: python models/nba/train_models.py")
            return False
        
        print(f"Found {len(model_files)} model files")
        
        # Check for at least one complete model set
        has_complete_set = False
        for prop_type in PROP_TYPES:
            lr_file = MODELS_DIR / f'{prop_type}_linear_regression.joblib'
            rf_file = MODELS_DIR / f'{prop_type}_random_forest.joblib'
            gb_file = MODELS_DIR / f'{prop_type}_gradient_boosting.joblib'
            scaler_file = MODELS_DIR / f'{prop_type}_scaler.joblib'
            
            if all([lr_file.exists(), rf_file.exists(), gb_file.exists(), scaler_file.exists()]):
                print(f"✓ Complete model set for {prop_type}")
                has_complete_set = True
                break
        
        return has_complete_set
    
    def test_5_load_predictor(self):
        """Test loading predictor"""
        predictor = NBAPredictor()
        
        if not predictor.models:
            print("No models loaded")
            return False
        
        print(f"Loaded models for {len(predictor.models)} prop types")
        print(f"Props: {', '.join(predictor.models.keys())}")
        return True
    
    def test_6_generate_prediction(self):
        """Test generating a single prediction"""
        predictor = NBAPredictor()
        
        # Get a game
        games = db_manager.execute_query("""
            SELECT id FROM games 
            WHERE sport = 'NBA' 
            ORDER BY date DESC 
            LIMIT 1
        """)
        
        if not games:
            print("No games to predict")
            return False
        
        game_id = games[0]['id']
        
        # Get a player
        players = db_manager.execute_query("""
            SELECT player_id FROM player_game_stats 
            WHERE game_id = %s 
            LIMIT 1
        """, (game_id,))
        
        if not players:
            print("No players to predict")
            return False
        
        player_id = players[0]['player_id']
        
        # Get first available prop type
        prop_type = list(predictor.models.keys())[0]
        
        # Generate prediction
        prediction = predictor.predict_single_player_prop(
            player_id, game_id, prop_type, is_home=True
        )
        
        if prediction is None:
            print("Could not generate prediction")
            return False
        
        print(f"Generated prediction for {prediction['player_name']}")
        print(f"  {prop_type}: {prediction['predicted_value']} "
              f"(confidence: {prediction['confidence_score']}%)")
        return True
    
    def test_7_value_finder(self):
        """Test value finder"""
        value_finder = ValueFinder()
        
        # Create dummy prediction
        prediction = {
            'player_id': 1,
            'player_name': 'Test Player',
            'prop_type': 'points',
            'game_date': '2024-10-19',
            'predicted_value': 25.5,
            'prediction_low': 22.0,
            'prediction_high': 29.0,
            'confidence_score': 75.0,
            'model_version': '1.0.0'
        }
        
        # Evaluate bet
        eval_result = value_finder.evaluate_bet(
            prediction,
            betting_line=23.5,
            odds=-110,
            bet_direction='over'
        )
        
        if eval_result is None:
            print("Value finder failed")
            return False
        
        print(f"Value evaluation:")
        print(f"  Edge: {eval_result['edge']:+.1f}")
        print(f"  EV: {eval_result['ev_pct']:+.1f}%")
        print(f"  Recommendation: {eval_result['recommendation']}")
        return True
    
    def test_8_save_to_database(self):
        """Test saving predictions to database"""
        predictor = NBAPredictor()
        
        # Create dummy prediction
        prediction = {
            'player_id': 1,
            'game_id': 1,
            'prop_type': 'points',
            'predicted_value': 25.5,
            'prediction_low': 22.0,
            'prediction_high': 29.0,
            'confidence_score': 75.0,
            'model_predictions': {
                'linear_regression': 25.0,
                'random_forest': 26.0,
                'gradient_boosting': 25.5
            },
            'model_version': '1.0.0'
        }
        
        # Try to save
        saved = predictor.save_predictions_to_db([prediction])
        
        if saved == 0:
            print("Could not save to database")
            return False
        
        print(f"Saved {saved} prediction(s)")
        return True
    
    def test_9_query_predictions(self):
        """Test querying predictions from database"""
        result = db_manager.execute_query("""
            SELECT COUNT(*) as count FROM projections
        """)
        
        if not result:
            print("Could not query projections table")
            return False
        
        count = result[0]['count']
        print(f"Found {count} projections in database")
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        
        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for name, status, error in self.results:
                if status == "FAIL":
                    print(f"  ✗ {name}")
                    if error:
                        print(f"    {error}")
        
        print("\n" + "="*60)
        
        if self.tests_failed == 0:
            print("✓ ALL TESTS PASSED!")
            print("="*60)
            return True
        else:
            print("✗ SOME TESTS FAILED")
            print("="*60)
            return False


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# NBA ML PREDICTION SYSTEM - COMPREHENSIVE TEST")
    print("#"*60)
    
    tester = SystemTester()
    
    try:
        # Run tests in order
        tester.run_test("1. Database Connection", tester.test_1_database_connection)
        tester.run_test("2. Data Availability", tester.test_2_data_availability)
        tester.run_test("3. Feature Engineering", tester.test_3_feature_engineering)
        tester.run_test("4. Models Exist", tester.test_4_models_exist)
        tester.run_test("5. Load Predictor", tester.test_5_load_predictor)
        tester.run_test("6. Generate Prediction", tester.test_6_generate_prediction)
        tester.run_test("7. Value Finder", tester.test_7_value_finder)
        tester.run_test("8. Save to Database", tester.test_8_save_to_database)
        tester.run_test("9. Query Predictions", tester.test_9_query_predictions)
        
        # Print summary
        success = tester.print_summary()
        
        if success:
            print("\n✓ System is ready to use!")
            print("\nNext steps:")
            print("  1. Generate predictions: python scripts/generate_nba_predictions.py")
            print("  2. View examples: python models/nba/example_usage.py")
            print("  3. Set up cron job for daily predictions")
            sys.exit(0)
        else:
            print("\n✗ System has issues that need to be fixed")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
