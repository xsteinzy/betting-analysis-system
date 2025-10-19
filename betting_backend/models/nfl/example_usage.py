#!/usr/bin/env python3
"""
Example Usage of NFL ML Prediction System

This script demonstrates how to use the NFL ML prediction system:
1. Train models
2. Generate predictions
3. Find value bets
4. Save to database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.db_manager import db_manager
from models.nfl.predict import NFLPredictor
from models.nfl.value_finder import ValueFinder
from models.nfl.train_models import ModelTrainer


def example_1_train_models():
    """Example 1: Train models for all prop types"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Train Models")
    print("="*60 + "\n")
    
    trainer = ModelTrainer()
    
    # Train just passing_yards for quick demo
    print("Training passing_yards model (demo)...")
    result = trainer.train_model_for_prop('passing_yards')
    
    if result:
        print("\n✓ Training successful!")
        print(f"Model MAE: {result['ensemble']['mae']:.3f}")
        print(f"Model R²: {result['ensemble']['r2']:.3f}")
    else:
        print("\n✗ Training failed - check if you have NFL data in database")


def example_2_generate_predictions():
    """Example 2: Generate predictions for upcoming games"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Generate Predictions")
    print("="*60 + "\n")
    
    predictor = NFLPredictor()
    
    # Predict this week's games
    print("Generating predictions for this week's games...")
    predictions = predictor.predict_week_games()
    
    if predictions:
        print(f"\n✓ Generated {len(predictions)} predictions")
        
        # Show sample predictions
        print("\nSample Predictions:")
        for pred in predictions[:5]:
            print(f"  {pred['player_name']} ({pred.get('position', '')}): {pred['prop_type']} = "
                  f"{pred['predicted_value']} (confidence: {pred['confidence_score']}%)")
    else:
        print("\n✗ No predictions generated - check if there are games this week")


def example_3_single_player_prediction():
    """Example 3: Predict a single player's performance"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Single Player Prediction")
    print("="*60 + "\n")
    
    predictor = NFLPredictor()
    
    # Get a random upcoming game
    games = db_manager.execute_query("""
        SELECT id, date, week, home_team_id, away_team_id
        FROM games
        WHERE sport = 'NFL' AND status IN ('scheduled', 'in_progress')
        ORDER BY date
        LIMIT 1
    """)
    
    if not games:
        print("✗ No upcoming games found")
        return
    
    game = games[0]
    
    # Get a QB from home team
    players = db_manager.execute_query("""
        SELECT id, name, position
        FROM players
        WHERE team_id = %s AND is_active = TRUE AND sport = 'NFL' AND position = 'QB'
        LIMIT 1
    """, (game['home_team_id'],))
    
    if not players:
        print("✗ No QB found")
        return
    
    player = players[0]
    
    print(f"Player: {player['name']}")
    print(f"Position: {player['position']}")
    print(f"Week: {game['week']}")
    print(f"Game Date: {game['date']}")
    print("\nPredictions:")
    
    # Predict QB-relevant props
    for prop_type in ['passing_yards', 'passing_touchdowns', 'interceptions', 'completions']:
        pred = predictor.predict_single_player_prop(
            player['id'],
            game['id'],
            prop_type,
            is_home=True
        )
        
        if pred:
            print(f"  {prop_type}: {pred['predicted_value']} "
                  f"(range: {pred['prediction_low']}-{pred['prediction_high']}, "
                  f"confidence: {pred['confidence_score']}%)")


def example_4_value_finder():
    """Example 4: Find value bets"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Value Finder")
    print("="*60 + "\n")
    
    predictor = NFLPredictor()
    value_finder = ValueFinder()
    
    # Generate predictions
    predictions = predictor.predict_week_games()
    
    if not predictions:
        print("✗ No predictions available")
        return
    
    # Example: Evaluate a bet
    sample_pred = predictions[0]
    
    # Simulate a betting line (in real usage, this comes from odds API)
    betting_line = sample_pred['predicted_value'] - 10.0  # Line 10 below prediction
    
    print(f"Player: {sample_pred['player_name']} ({sample_pred.get('position', '')})")
    print(f"Prop: {sample_pred['prop_type']}")
    print(f"Prediction: {sample_pred['predicted_value']}")
    print(f"Betting Line: {betting_line}")
    
    # Evaluate over bet
    over_eval = value_finder.evaluate_bet(
        sample_pred,
        betting_line,
        odds=-110,
        bet_direction='over'
    )
    
    if over_eval:
        print(f"\nOVER Bet Analysis:")
        print(f"  Edge: {over_eval['edge']:+.1f}")
        print(f"  Expected Value: {over_eval['ev_pct']:+.1f}%")
        print(f"  Win Probability: {over_eval['win_probability']}%")
        print(f"  Value Rating: {over_eval['value_rating']}")
        print(f"  Recommendation: {over_eval['recommendation']}")
        print(f"  Reasoning: {over_eval['reasoning']}")


def example_5_save_to_database():
    """Example 5: Save predictions to database"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Save Predictions to Database")
    print("="*60 + "\n")
    
    predictor = NFLPredictor()
    
    # Generate predictions
    predictions = predictor.predict_week_games()
    
    if predictions:
        print(f"Generated {len(predictions)} predictions")
        
        # Save to database
        saved_count = predictor.save_predictions_to_db(predictions)
        
        print(f"✓ Saved {saved_count} predictions to database")
        
        # Query recent predictions
        recent = db_manager.execute_query("""
            SELECT 
                p.name as player_name,
                p.position,
                proj.prop_type,
                proj.projected_value,
                proj.confidence,
                g.week
            FROM projections proj
            JOIN players p ON proj.player_id = p.id
            JOIN games g ON proj.game_id = g.id
            WHERE p.sport = 'NFL'
            AND DATE(proj.created_at) = CURRENT_DATE
            ORDER BY proj.confidence DESC
            LIMIT 5
        """)
        
        if recent:
            print("\nTop 5 High Confidence Predictions from Database:")
            for pred in recent:
                print(f"  {pred['player_name']} ({pred.get('position', '')}): {pred['prop_type']} = "
                      f"{pred['projected_value']} (confidence: {pred['confidence']}%, Week {pred.get('week', '')})")
    else:
        print("✗ No predictions generated")


def example_6_find_best_values():
    """Example 6: Find best value bets across all predictions"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Find Best Value Bets")
    print("="*60 + "\n")
    
    predictor = NFLPredictor()
    value_finder = ValueFinder()
    
    # Generate predictions
    predictions = predictor.predict_week_games()
    
    if not predictions:
        print("✗ No predictions available")
        return
    
    # Simulate betting lines (in real usage, fetch from odds API)
    betting_lines = {}
    for pred in predictions:
        player_id = pred['player_id']
        prop_type = pred['prop_type']
        
        if player_id not in betting_lines:
            betting_lines[player_id] = {}
        
        # Simulate line (slightly below prediction for demo)
        if 'yards' in prop_type:
            betting_lines[player_id][prop_type] = pred['predicted_value'] - 15
        elif 'touchdowns' in prop_type:
            betting_lines[player_id][prop_type] = pred['predicted_value'] - 0.5
        else:
            betting_lines[player_id][prop_type] = pred['predicted_value'] - 2
    
    # Find best values
    best_values = value_finder.find_best_values(
        predictions,
        betting_lines,
        min_confidence=60,
        top_n=10
    )
    
    if best_values:
        print(f"Found {len(best_values)} value bets:\n")
        
        for i, bet in enumerate(best_values[:5], 1):
            print(f"{i}. {bet['player_name']} ({bet.get('position', '')}) - {bet['prop_type']} {bet['bet_direction']}")
            print(f"   Week: {bet.get('week', '')}")
            print(f"   Prediction: {bet['predicted_value']} | Line: {bet['betting_line']}")
            print(f"   Edge: {bet['edge']:+.1f} | EV: {bet['ev_pct']:+.1f}%")
            print(f"   Confidence: {bet['confidence']}% | {bet['value_rating']}")
            print(f"   → {bet['recommendation']}\n")
    else:
        print("✗ No value bets found")


def main():
    """Run all examples"""
    print("\n" + "#"*60)
    print("# NFL ML PREDICTION SYSTEM - EXAMPLE USAGE")
    print("#"*60)
    
    try:
        # Check if models exist
        from models.nfl.config import MODELS_DIR
        model_files = list(MODELS_DIR.glob('*.joblib'))
        
        if not model_files:
            print("\n⚠️  No trained models found!")
            print("Running Example 1 to train a model first...\n")
            example_1_train_models()
            print("\nNow run this script again to see all examples.")
            return
        
        print("\n✓ Models found. Running examples...\n")
        
        # Run examples
        # example_1_train_models()  # Skip training in demo
        example_2_generate_predictions()
        example_3_single_player_prediction()
        example_4_value_finder()
        example_5_save_to_database()
        example_6_find_best_values()
        
        print("\n" + "#"*60)
        print("# All examples completed!")
        print("#"*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
