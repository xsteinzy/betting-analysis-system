#!/usr/bin/env python3
"""
Test NFL ML Prediction System

Comprehensive test script to verify the entire NFL system is working correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager
from models.nfl.config import PROP_TYPES, MODELS_DIR
from models.nfl.predict import NFLPredictor
from models.nfl.value_finder import ValueFinder
from models.nfl.train_models import ModelTrainer
from models.nfl.feature_engineering import NFLFeatureEngineer


class NFLSystemTester:
    """Test the NFL ML prediction system"""
    
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
        """Test if sufficient NFL data exists"""
        # Check for games
        games = db_manager.execute_query("""
            SELECT COUNT(*) as count FROM games WHERE sport = 'NFL'
        """)
        
        if not games or games[0]['count'] == 0:
            print("No NFL games in database")
            return False
        
        print(f"Found {games[0]['count']} NFL games")
        
        # Check for player stats
        stats = db_manager.execute_query("""
            SELECT COUNT(*) as count 
            FROM player_game_stats pgs
            JOIN players p ON pgs.player_id = p.id
            WHERE p.sport = 'NFL'
        """)
        
        if not stats or stats[0]['count'] < 50:
            print(f"Insufficient NFL player stats: {stats[0]['count'] if stats else 0}")
            return False
        
        print(f"Found {stats[0]['count']} NFL player game stats")
        return True
    
    def test_3_feature_engineering(self):
        """Test feature engineering"""
        engineer = NFLFeatureEngineer()
        
        # Get an NFL player with stats
        player_stats = db_manager.execute_query("""
            SELECT DISTINCT pgs.player_id, pgs.game_id, pgs.is_home
            FROM player_game_stats pgs
            JOIN players p ON pgs.player_id = p.id
            WHERE p.sport = 'NFL'
            LIMIT 1
        """)
        
        if not player_stats:
            print("No NFL player stats to test with")
            return False
        
        player = player_stats[0]
        
        # Try to extract features
        features = engineer.extract_features_for_player(
            player['player_id'],
            player['game_id'],
            db_manager,
            player['is_home'],
            'passing_yards'
        )
        
        if features is None:
            print("Feature extraction returned None")
            return False
        
        print(f"Extracted {len(features)} features")
        
        # Check for required features
        required_features = ['avg_3_games', 'avg_5_games', 'season_avg', 'is_home']
        for feat in required_features:
            if feat not in features:
                print(f"Missing required feature: {feat}")
                return False
        
        return True
    
    def test_4_models_exist(self):
        """Test if trained models exist"""
        model_files = list(MODELS_DIR.glob('*.joblib'))
        
        if not model_files:
            print("No trained models found")
            print("Run: python models/nfl/train_models.py")
            return False
        
        print(f"Found {len(model_files)} model files")
        return True
    
    def test_5_load_models(self):
        """Test loading trained models"""
        predictor = NFLPredictor()
        
        if not predictor.models:
            print("No models loaded")
            return False
        
        print(f"Loaded models for {len(predictor.models)} prop types")
        
        # Check each loaded model
        for prop_type, models in predictor.models.items():
            required_models = ['linear_regression', 'random_forest', 'gradient_boosting']
            for model_name in required_models:
                if model_name not in models:
                    print(f"Missing {model_name} for {prop_type}")
                    return False
        
        return True
    
    def test_6_single_prediction(self):
        """Test generating a single prediction"""
        predictor = NFLPredictor()
        
        if not predictor.models:
            print("No models loaded - train models first")
            return False
        
        # Get an upcoming NFL game
        games = db_manager.execute_query("""
            SELECT g.id, g.home_team_id
            FROM games g
            WHERE g.sport = 'NFL'
            AND g.status IN ('scheduled', 'in_progress')
            ORDER BY g.date
            LIMIT 1
        """)
        
        if not games:
            print("No upcoming NFL games found")
            return False
        
        game = games[0]
        
        # Get a QB from home team
        players = db_manager.execute_query("""
            SELECT id FROM players
            WHERE team_id = %s 
            AND sport = 'NFL'
            AND position = 'QB'
            AND is_active = TRUE
            LIMIT 1
        """, (game['home_team_id'],))
        
        if not players:
            print("No QB found for home team")
            return False
        
        player_id = players[0]['id']
        
        # Generate prediction
        prediction = predictor.predict_single_player_prop(
            player_id,
            game['id'],
            'passing_yards',
            is_home=True
        )
        
        if prediction is None:
            print("Prediction returned None")
            return False
        
        print(f"Generated prediction: {prediction['predicted_value']}")
        print(f"Confidence: {prediction['confidence_score']}%")
        
        # Validate prediction structure
        required_fields = ['predicted_value', 'confidence_score', 'player_name', 'prop_type']
        for field in required_fields:
            if field not in prediction:
                print(f"Missing field: {field}")
                return False
        
        return True
    
    def test_7_game_predictions(self):
        """Test generating predictions for a game"""
        predictor = NFLPredictor()
        
        if not predictor.models:
            print("No models loaded")
            return False
        
        # Get an upcoming game
        games = db_manager.execute_query("""
            SELECT id FROM games
            WHERE sport = 'NFL'
            AND status IN ('scheduled', 'in_progress')
            ORDER BY date
            LIMIT 1
        """)
        
        if not games:
            print("No upcoming NFL games found")
            return False
        
        game_id = games[0]['id']
        
        # Generate predictions for the game
        predictions = predictor.predict_game(game_id)
        
        if not predictions:
            print("No predictions generated")
            return False
        
        print(f"Generated {len(predictions)} predictions for the game")
        
        # Group by position
        by_position = {}
        for pred in predictions:
            pos = pred.get('position', 'Unknown')
            by_position[pos] = by_position.get(pos, 0) + 1
        
        print(f"Predictions by position: {by_position}")
        
        return True
    
    def test_8_value_finder(self):
        """Test value finder functionality"""
        value_finder = ValueFinder()
        
        # Create a sample prediction
        sample_prediction = {
            'player_id': 1,
            'player_name': 'Test QB',
            'position': 'QB',
            'game_id': 1,
            'game_date': '2024-10-19',
            'week': 7,
            'prop_type': 'passing_yards',
            'predicted_value': 285.5,
            'prediction_low': 250.0,
            'prediction_high': 320.0,
            'confidence_score': 75.0,
            'model_version': '1.0.0'
        }
        
        betting_line = 265.5
        
        # Evaluate bet
        evaluation = value_finder.evaluate_bet(
            sample_prediction,
            betting_line,
            odds=-110,
            bet_direction='over'
        )
        
        if evaluation is None:
            print("Value finder returned None")
            return False
        
        print(f"Edge: {evaluation['edge']}")
        print(f"EV%: {evaluation['ev_pct']}")
        print(f"Recommendation: {evaluation['recommendation']}")
        
        # Check required fields
        required_fields = ['edge', 'ev_pct', 'recommendation', 'value_rating']
        for field in required_fields:
            if field not in evaluation:
                print(f"Missing field: {field}")
                return False
        
        return True
    
    def test_9_save_to_database(self):
        """Test saving predictions to database"""
        predictor = NFLPredictor()
        
        if not predictor.models:
            print("No models loaded")
            return False
        
        # Generate predictions
        predictions = predictor.predict_week_games()
        
        if not predictions:
            print("No predictions to save")
            return False
        
        # Take first prediction for testing
        test_predictions = predictions[:1]
        
        # Save to database
        saved_count = predictor.save_predictions_to_db(test_predictions)
        
        if saved_count == 0:
            print("Failed to save predictions")
            return False
        
        print(f"Saved {saved_count} prediction(s)")
        
        # Verify in database
        verification = db_manager.execute_query("""
            SELECT COUNT(*) as count
            FROM projections
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        
        if not verification or verification[0]['count'] == 0:
            print("Predictions not found in database")
            return False
        
        print(f"Verified {verification[0]['count']} predictions in database")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "#"*60)
        print("# NFL ML SYSTEM TEST SUITE")
        print("#"*60)
        
        self.run_test("1. Database Connection", self.test_1_database_connection)
        self.run_test("2. Data Availability", self.test_2_data_availability)
        self.run_test("3. Feature Engineering", self.test_3_feature_engineering)
        self.run_test("4. Models Exist", self.test_4_models_exist)
        self.run_test("5. Load Models", self.test_5_load_models)
        self.run_test("6. Single Prediction", self.test_6_single_prediction)
        self.run_test("7. Game Predictions", self.test_7_game_predictions)
        self.run_test("8. Value Finder", self.test_8_value_finder)
        self.run_test("9. Save to Database", self.test_9_save_to_database)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Total: {self.tests_passed + self.tests_failed}")
        print("="*60)
        
        # Print failed tests
        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for name, status, error in self.results:
                if status == "FAIL":
                    print(f"  ✗ {name}")
                    if error:
                        print(f"    Error: {error}")
        
        return self.tests_failed == 0


def main():
    """Main function"""
    tester = NFLSystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n✓ All tests passed!")
            print("\nNFL ML system is working correctly.")
            print("You can now:")
            print("  - Generate predictions: python scripts/generate_nfl_predictions.py")
            print("  - Run examples: python models/nfl/example_usage.py")
            print("  - View documentation: cat models/nfl/README.md")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed.")
            print("\nPlease fix the issues before using the system.")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
