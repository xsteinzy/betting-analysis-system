# NFL Machine Learning Prediction System

A complete machine learning system for predicting NFL player props and identifying value bets.

## 🎯 Overview

This system uses ensemble machine learning to predict 10 different NFL player prop types:

1. **Passing Yards** - Total passing yards (QB)
2. **Rushing Yards** - Total rushing yards (RB, QB)
3. **Receiving Yards** - Total receiving yards (WR, TE, RB)
4. **Passing Touchdowns** - Passing touchdowns (QB)
5. **Rushing Touchdowns** - Rushing touchdowns (RB, QB)
6. **Receiving Touchdowns** - Receiving touchdowns (WR, TE, RB)
7. **Receptions** - Total receptions (WR, TE, RB)
8. **Interceptions** - Interceptions thrown (QB)
9. **Completions** - Pass completions (QB)
10. **Field Goals Made** - Field goals made (K)

### Key Features

- ✅ **Ensemble Learning**: Combines Linear Regression, Random Forest, and Gradient Boosting
- ✅ **Advanced Feature Engineering**: Rolling averages, home/away splits, rest days, trends
- ✅ **Position-Aware**: Predicts only relevant props for each position (QB, RB, WR, TE, K)
- ✅ **Confidence Scoring**: 0-100 score based on model agreement and data quality
- ✅ **Value Finder**: Compare predictions to betting lines and calculate expected value
- ✅ **Weekly Schedule**: Optimized for NFL's weekly format
- ✅ **Production Ready**: Save/load models, automated pipeline, comprehensive logging

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Training Models](#training-models)
- [Generating Predictions](#generating-predictions)
- [Value Finder](#value-finder)
- [Model Architecture](#model-architecture)
- [Feature Engineering](#feature-engineering)
- [Performance Metrics](#performance-metrics)
- [NFL-Specific Considerations](#nfl-specific-considerations)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🔧 Installation

### 1. Install ML Dependencies

```bash
cd /home/ubuntu/betting_backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import sklearn, xgboost, joblib; print('✓ ML dependencies installed')"
```

## 🚀 Quick Start

### Step 1: Ensure You Have Data

You need historical NFL player game stats to train models:

```bash
# Collect historical NFL data
python collect_data.py --sport NFL
```

### Step 2: Train Models

Train models for all prop types:

```bash
python models/nfl/train_models.py
```

For testing with just one prop type:

```bash
python models/nfl/train_models.py --test
```

### Step 3: Generate Predictions

Generate predictions for this week's games:

```bash
python scripts/generate_nfl_predictions.py
```

That's it! Your predictions are now saved to the database.

## 📊 Training Models

### Basic Training

Train models for all prop types:

```bash
python models/nfl/train_models.py
```

### Train Specific Props

Train only specific prop types:

```bash
python models/nfl/train_models.py --prop-types passing_yards rushing_yards receiving_yards
```

### Understanding Training Output

The training process will:

1. **Load Data**: Fetch historical NFL player stats from database
2. **Feature Engineering**: Create features (rolling averages, trends, etc.)
3. **Train Models**: Train 3 models per prop type (Linear Regression, Random Forest, Gradient Boosting)
4. **Cross-Validation**: 5-fold CV on training set
5. **Evaluation**: Test on held-out test set (20% of data)
6. **Save Models**: Save trained models to `models/nfl/saved_models/`

### Example Output

```
Training models for passing_yards
Train size: 250, Test size: 62

LINEAR REGRESSION:
  MAE: 32.4
  RMSE: 45.2
  R²: 0.68
  Within 20 yards: 48.3%

RANDOM FOREST:
  MAE: 28.7
  RMSE: 40.8
  R²: 0.74
  Within 20 yards: 53.2%

GRADIENT BOOSTING:
  MAE: 27.5
  RMSE: 39.1
  R²: 0.76
  Within 20 yards: 55.6%

ENSEMBLE (Average):
  MAE: 26.8
  RMSE: 38.2
  R²: 0.78
  Within 20 yards: 57.1%
```

## 🔮 Generating Predictions

### Weekly Predictions Script

The main script for weekly predictions:

```bash
# Predict current week's games
python scripts/generate_nfl_predictions.py

# Predict specific week
python scripts/generate_nfl_predictions.py --week 7

# Predict only specific props
python scripts/generate_nfl_predictions.py --prop-types passing_yards rushing_yards

# Retrain models before predicting
python scripts/generate_nfl_predictions.py --retrain
```

### Unified Multi-Sport Script

Generate predictions for both NFL and NBA:

```bash
# Generate for both sports
python scripts/generate_predictions.py --sport both

# NFL only
python scripts/generate_predictions.py --sport nfl --week 7

# NBA only
python scripts/generate_predictions.py --sport nba --date 2024-10-25
```

### Python API Usage

Generate predictions programmatically:

```python
from models.nfl.predict import NFLPredictor
from database.db_manager import db_manager

# Create predictor
predictor = NFLPredictor()

# Predict current week
predictions = predictor.predict_week_games()

# Predict specific week
predictions = predictor.predict_week_games(week=7)

# Predict specific game
game_predictions = predictor.predict_game(game_id=123)

# Predict single player
single_pred = predictor.predict_single_player_prop(
    player_id=456,
    game_id=123,
    prop_type='passing_yards',
    is_home=True
)

# Save to database
predictor.save_predictions_to_db(predictions)

db_manager.close()
```

### Prediction Output Format

Each prediction contains:

```python
{
    'player_id': 456,
    'player_name': 'Patrick Mahomes',
    'position': 'QB',
    'game_id': 123,
    'game_date': '2024-10-19',
    'week': 7,
    'is_home': True,
    'prop_type': 'passing_yards',
    'predicted_value': 285.5,
    'prediction_low': 250.0,
    'prediction_high': 320.0,
    'confidence_score': 78.5,
    'model_predictions': {
        'linear_regression': 280.2,
        'random_forest': 289.1,
        'gradient_boosting': 287.2
    },
    'model_version': '1.0.0',
    'created_at': '2024-10-19T08:30:00'
}
```

## 💎 Value Finder

Compare predictions to betting lines and identify value bets.

### Python API Usage

```python
from models.nfl.predict import NFLPredictor
from models.nfl.value_finder import ValueFinder

# Get predictions
predictor = NFLPredictor()
predictions = predictor.predict_week_games()

# Create value finder
value_finder = ValueFinder()

# Evaluate a bet
prediction = predictions[0]
betting_line = 265.5  # Bookmaker's line
odds = -110

over_bet = value_finder.evaluate_bet(
    prediction=prediction,
    betting_line=betting_line,
    odds=odds,
    bet_direction='over'
)

print(f"Player: {over_bet['player_name']} ({over_bet['position']})")
print(f"Week: {over_bet['week']}")
print(f"Expected Value: {over_bet['ev_pct']:+.1f}%")
print(f"Recommendation: {over_bet['recommendation']}")
```

## 🏗️ Model Architecture

### Ensemble Approach

Each prop type uses 3 models:

1. **Linear Regression** - Fast baseline
2. **Random Forest** - Non-linear relationships, 100 trees
3. **Gradient Boosting (XGBoost)** - Best predictive performance

**Final Prediction** = Average of all 3 models

## 🛠️ Feature Engineering

### Core Features (18 total)

1. **Rolling Averages**: Last 3, 5, 10 games
2. **Home/Away Splits**: Separate averages for home/away games
3. **Rest Days**: Days since last game (typically 6-7 for NFL)
4. **Recent Form**: Trend analysis over recent games
5. **Consistency**: Standard deviation and consistency score
6. **Snaps**: Average snaps in recent games (NFL-specific)
7. **Season Stats**: Games played, season average
8. **Opponent Metrics**: Defensive ratings (placeholder for enhancement)

### Position-Specific Props

The system only predicts relevant props for each position:

- **QB**: Passing yards, passing TDs, interceptions, completions, rushing yards
- **RB**: Rushing yards, rushing TDs, receiving yards, receptions, receiving TDs
- **WR**: Receiving yards, receptions, receiving TDs
- **TE**: Receiving yards, receptions, receiving TDs
- **K**: Field goals made

## 📈 Performance Metrics

### Typical Model Performance

Based on training with sufficient data:

| Prop Type | Ensemble MAE | R² | Within Threshold |
|-----------|-------------|-----|------------------|
| Passing Yards | 28 | 0.75 | 56% (±20 yards) |
| Rushing Yards | 18 | 0.68 | 58% (±15 yards) |
| Receiving Yards | 15 | 0.70 | 60% (±15 yards) |
| Passing TDs | 0.7 | 0.62 | 65% (±1 TD) |
| Receptions | 1.2 | 0.68 | 62% (±2) |

*Performance depends on data quality and quantity*

## 🏈 NFL-Specific Considerations

### Weekly Schedule

- NFL plays once per week (typically Sunday)
- Less data per season (17 games vs NBA's 82)
- Requires lower minimum games threshold (5 vs 10 for NBA)

### Position Importance

- Position determines relevant props
- QB props have highest volume
- RB/WR/TE share receiving props
- Kickers have unique props

### Season Length

- Shorter season means less training data
- Feature windows adjusted (3/5/10 games instead of larger windows)
- Cross-season data may be more valuable

### Bye Weeks

- Teams have one bye week per season
- Predictions not generated for bye weeks
- Rest days calculation accounts for bye weeks

## ⚙️ Configuration

Edit `models/nfl/config.py` to customize:

```python
# Prop types to predict
PROP_TYPES = ['passing_yards', 'rushing_yards', ...]

# Position-specific props
POSITION_PROP_MAPPING = {
    'QB': ['passing_yards', 'passing_touchdowns', ...],
    'RB': ['rushing_yards', 'rushing_touchdowns', ...],
    ...
}

# Training parameters
TRAINING_CONFIG = {
    'test_size': 0.2,
    'min_games_required': 5,  # Lower for NFL
    'cv_folds': 5
}

# Value bet thresholds
VALUE_BET_CONFIG = {
    'strong_value_threshold': 5.0,
    'moderate_value_threshold': 2.0,
    'min_confidence_for_bet': 60,
    'min_edge_for_recommendation': 5.0  # Higher for NFL yards
}
```

## 🔍 Troubleshooting

### "No training examples created"

**Problem**: Not enough NFL data

**Solution**:
```bash
python collect_data.py --sport NFL
```

You need at least 50+ player game stats to train models.

### "Models for X not found"

**Problem**: Models haven't been trained

**Solution**:
```bash
python models/nfl/train_models.py
```

### Low Model Performance

**Causes**:
1. Not enough training data (NFL season is shorter)
2. Position-specific data issues
3. Week-to-week variance is high in NFL

**Solutions**:
1. Collect multiple seasons of data
2. Use cross-season data
3. Tune hyperparameters for specific positions

## 📚 Additional Resources

### Files and Directories

```
models/nfl/
├── __init__.py
├── config.py                  # NFL-specific configuration
├── feature_engineering.py     # Feature extraction for NFL
├── train_models.py           # Training pipeline
├── predict.py                # Prediction engine
├── value_finder.py           # Value bet analyzer
├── example_usage.py          # Usage examples
├── saved_models/             # Trained model files
└── README.md                 # This file

scripts/
├── generate_nfl_predictions.py  # Weekly NFL predictions
└── generate_predictions.py      # Unified multi-sport script
```

### Related Documentation

- [NFL Quick Start Guide](../../NFL_QUICKSTART.md)
- [NBA ML System](../nba/README.md)
- [Main Backend README](../../README.md)
- [ML System Summary](../../ML_SYSTEM_SUMMARY.md)

## 📝 Notes

- Models require at least 5 games per player to train (vs 10 for NBA)
- Predictions are more reliable mid-season with more data
- Rookie players may not have predictions early in season
- Position-specific props ensure relevance
- Weekly schedule means predictions typically run Tuesday-Saturday

---

**Disclaimer**: This system is for educational and research purposes. Sports betting involves risk. Always bet responsibly and within your means.
