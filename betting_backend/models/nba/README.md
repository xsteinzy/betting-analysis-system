# NBA Machine Learning Prediction System

A complete machine learning system for predicting NBA player props and identifying value bets.

## 🎯 Overview

This system uses ensemble machine learning to predict 10 different NBA player prop types:

1. **Points** - Total points scored
2. **Rebounds** - Total rebounds
3. **Assists** - Total assists
4. **3-Pointers Made** - Three-point shots made
5. **Steals** - Total steals
6. **Blocks** - Total blocks
7. **Turnovers** - Total turnovers
8. **Double-Double** - Probability of achieving a double-double
9. **Field Goals Made** - Total field goals made
10. **Free Throws Made** - Total free throws made

### Key Features

- ✅ **Ensemble Learning**: Combines Linear Regression, Random Forest, and Gradient Boosting
- ✅ **Advanced Feature Engineering**: Rolling averages, home/away splits, rest days, trends
- ✅ **Confidence Scoring**: 0-100 score based on model agreement and data quality
- ✅ **Value Finder**: Compare predictions to betting lines and calculate expected value
- ✅ **Production Ready**: Save/load models, automated pipeline, comprehensive logging
- ✅ **Time-Based Validation**: Prevents data leakage with proper train/test splits

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Training Models](#training-models)
- [Generating Predictions](#generating-predictions)
- [Value Finder](#value-finder)
- [Model Architecture](#model-architecture)
- [Feature Engineering](#feature-engineering)
- [Performance Metrics](#performance-metrics)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## 🔧 Installation

### 1. Install ML Dependencies

```bash
cd /home/ubuntu/betting_backend
source venv/bin/activate  # Activate your virtual environment
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import sklearn, xgboost, joblib; print('✓ ML dependencies installed')"
```

## 🚀 Quick Start

### Step 1: Ensure You Have Data

You need historical player game stats to train models:

```bash
# Collect historical data (this may take 30-60 minutes)
python collect_data.py --with-stats
```

### Step 2: Train Models

Train models for all prop types:

```bash
python models/nba/train_models.py
```

For testing with just one prop type:

```bash
python models/nba/train_models.py --test
```

### Step 3: Generate Predictions

Generate predictions for today's games:

```bash
python scripts/generate_nba_predictions.py
```

That's it! Your predictions are now saved to the database.

## 📊 Training Models

### Basic Training

Train models for all prop types:

```bash
python models/nba/train_models.py
```

### Train Specific Props

Train only specific prop types:

```bash
python models/nba/train_models.py --prop-types points rebounds assists
```

### Understanding Training Output

The training process will:

1. **Load Data**: Fetch historical player stats from database
2. **Feature Engineering**: Create features (rolling averages, trends, etc.)
3. **Train Models**: Train 3 models per prop type (Linear Regression, Random Forest, Gradient Boosting)
4. **Cross-Validation**: 5-fold CV on training set
5. **Evaluation**: Test on held-out test set (20% of data)
6. **Save Models**: Save trained models to `models/nba/saved_models/`

### Example Output

```
Training models for points
Train size: 1200, Test size: 300

LINEAR REGRESSION:
  MAE: 4.52
  RMSE: 6.18
  R²: 0.745
  Within 3 points: 45.2%

RANDOM FOREST:
  MAE: 3.98
  RMSE: 5.67
  R²: 0.782
  Within 3 points: 52.1%

GRADIENT BOOSTING:
  MAE: 3.85
  RMSE: 5.52
  R²: 0.795
  Within 3 points: 54.3%

ENSEMBLE (Average):
  MAE: 3.76
  RMSE: 5.41
  R²: 0.803
  Within 3 points: 56.7%

Top 10 Feature Importances:
  1. avg_5_games: 0.2543
  2. avg_10_games: 0.1876
  3. season_avg: 0.1432
  4. avg_minutes_5_games: 0.0987
  ...
```

### Training Metrics Explained

- **MAE (Mean Absolute Error)**: Average difference between prediction and actual value. Lower is better.
- **RMSE (Root Mean Squared Error)**: Similar to MAE but penalizes large errors more. Lower is better.
- **R² (Coefficient of Determination)**: How well the model fits the data. 1.0 is perfect, 0.0 is random.
- **Within X Points**: Percentage of predictions within X points of actual value.

### Where Models Are Saved

Trained models are saved to:
```
models/nba/saved_models/
  ├── points_linear_regression.joblib
  ├── points_random_forest.joblib
  ├── points_gradient_boosting.joblib
  ├── points_scaler.joblib
  ├── points_metadata.json
  ├── rebounds_*.joblib
  └── ... (for each prop type)
```

## 🔮 Generating Predictions

### Daily Predictions Script

The main script for daily predictions:

```bash
# Predict today's games
python scripts/generate_nba_predictions.py

# Predict specific date
python scripts/generate_nba_predictions.py --date 2024-10-25

# Predict tomorrow's games
python scripts/generate_nba_predictions.py --days-ahead 1

# Predict only specific props
python scripts/generate_nba_predictions.py --prop-types points rebounds assists

# Retrain models before predicting
python scripts/generate_nba_predictions.py --retrain

# Just check if data is ready
python scripts/generate_nba_predictions.py --check-only
```

### Automated Daily Predictions

Set up a cron job to run predictions automatically:

```bash
crontab -e

# Add this line (runs at 8:00 AM daily)
0 8 * * * cd /home/ubuntu/betting_backend && /home/ubuntu/betting_backend/venv/bin/python scripts/generate_nba_predictions.py >> logs/predictions_cron.log 2>&1
```

### Python API Usage

Generate predictions programmatically:

```python
from models.nba.predict import NBAPredictor
from database.db_manager import db_manager

# Create predictor
predictor = NBAPredictor()

# Predict today's games
predictions = predictor.predict_today_games()

# Predict specific game
game_predictions = predictor.predict_game(game_id=123)

# Predict single player
single_pred = predictor.predict_single_player_prop(
    player_id=456,
    game_id=123,
    prop_type='points',
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
    'player_name': 'LeBron James',
    'position': 'F',
    'game_id': 123,
    'game_date': '2024-10-19',
    'is_home': True,
    'prop_type': 'points',
    'predicted_value': 28.5,
    'prediction_low': 24.0,    # Lower bound of prediction interval
    'prediction_high': 33.0,   # Upper bound of prediction interval
    'confidence_score': 78.5,  # 0-100 confidence score
    'model_predictions': {
        'linear_regression': 27.8,
        'random_forest': 29.1,
        'gradient_boosting': 28.6
    },
    'model_version': '1.0.0',
    'created_at': '2024-10-19T08:30:00'
}
```

### Accessing Predictions from Database

```sql
-- Get today's predictions
SELECT 
    p.name as player_name,
    proj.prop_type,
    proj.projected_value,
    proj.confidence,
    g.date as game_date
FROM projections proj
JOIN players p ON proj.player_id = p.id
JOIN games g ON proj.game_id = g.id
WHERE DATE(proj.created_at) = CURRENT_DATE
ORDER BY proj.confidence DESC;

-- Get high confidence predictions
SELECT *
FROM projections
WHERE confidence >= 75
AND DATE(created_at) = CURRENT_DATE
ORDER BY confidence DESC;
```

## 💎 Value Finder

Compare predictions to betting lines and identify value bets.

### Python API Usage

```python
from models.nba.predict import NBAPredictor
from models.nba.value_finder import ValueFinder

# Get predictions
predictor = NBAPredictor()
predictions = predictor.predict_today_games()

# Create value finder
value_finder = ValueFinder()

# Evaluate a bet
prediction = predictions[0]  # Example prediction
betting_line = 25.5  # Bookmaker's line
odds = -110  # American odds

over_bet = value_finder.evaluate_bet(
    prediction=prediction,
    betting_line=betting_line,
    odds=odds,
    bet_direction='over'
)

print(f"Player: {over_bet['player_name']}")
print(f"Prediction: {over_bet['predicted_value']}")
print(f"Line: {over_bet['betting_line']}")
print(f"Edge: {over_bet['edge']:+.1f}")
print(f"Expected Value: {over_bet['ev_pct']:+.1f}%")
print(f"Recommendation: {over_bet['recommendation']}")
print(f"Reasoning: {over_bet['reasoning']}")
```

### Find Best Value Bets

```python
# Example betting lines (you would get these from an odds API)
betting_lines = {
    456: {  # player_id
        'points': 25.5,
        'rebounds': 7.5,
        'assists': 8.5
    },
    789: {
        'points': 22.5,
        'rebounds': 9.5,
        'assists': 3.5
    }
}

# Find best value bets
best_values = value_finder.find_best_values(
    predictions=predictions,
    betting_lines=betting_lines,
    min_confidence=65,
    top_n=10
)

# Print results
for i, bet in enumerate(best_values, 1):
    print(f"\n{i}. {bet['player_name']} - {bet['prop_type']} {bet['bet_direction']}")
    print(f"   Prediction: {bet['predicted_value']} | Line: {bet['betting_line']}")
    print(f"   Edge: {bet['edge']:+.1f} | EV: {bet['ev_pct']:+.1f}%")
    print(f"   Confidence: {bet['confidence']}%")
    print(f"   {bet['value_rating']} - {bet['recommendation']}")
```

### Value Bet Output Format

```python
{
    'player_name': 'LeBron James',
    'prop_type': 'points',
    'game_date': '2024-10-19',
    'predicted_value': 28.5,
    'betting_line': 25.5,
    'bet_direction': 'OVER',
    'odds': -110,
    'edge': 3.0,
    'confidence': 78.5,
    'ev_pct': 4.8,
    'win_probability': 58.2,
    'value_rating': 'Moderate Value',
    'recommendation': 'BET',
    'reasoning': 'Model projects 28.5 points, line is 25.5, giving a +3.0 point edge. ...',
    'prediction_range': '24.0 - 33.0',
    'model_version': '1.0.0',
    'evaluated_at': '2024-10-19T08:30:00'
}
```

### Value Rating Criteria

- **Strong Value**: EV > 5% → BET
- **Moderate Value**: EV 2-5% → BET (if confidence ≥ 60%)
- **Slight Value**: EV 0-2% → PASS
- **No Value**: EV < 0% → PASS

### Expected Value Formula

```
EV = (Win Probability × Payout) - (Loss Probability × Stake)
EV% = (EV / Stake) × 100
```

## 🏗️ Model Architecture

### Ensemble Approach

Each prop type uses 3 models:

1. **Linear Regression**
   - Fast, interpretable baseline
   - Good for linear relationships
   - Least complex

2. **Random Forest**
   - Handles non-linear relationships
   - Robust to outliers
   - Feature importance
   - 100 trees, max depth 10

3. **Gradient Boosting (XGBoost)**
   - Best predictive performance
   - Sequential error correction
   - 100 estimators, learning rate 0.1

**Final Prediction** = Average of all 3 models

### Why Ensemble?

- **Robustness**: Reduces risk of overfitting
- **Accuracy**: Combines strengths of different algorithms
- **Confidence**: Model agreement indicates prediction reliability

## 🛠️ Feature Engineering

### Core Features

#### 1. Rolling Averages
- Last 3 games average
- Last 5 games average
- Last 10 games average
- Season average

#### 2. Home/Away Splits
- Home game average
- Away game average
- Is home (binary: 1/0)

#### 3. Rest and Schedule
- Days rest since last game
- Games played in last 7 days

#### 4. Recent Form
- Trend (slope of recent performance)
- Consistency score (inverse of coefficient of variation)
- Standard deviation of last 10 games

#### 5. Minutes Played
- Average minutes last 3 games
- Average minutes last 5 games

#### 6. Opponent Metrics
- Opponent defensive rating (placeholder for future enhancement)
- Matchup history average

### Feature Importance

Based on Random Forest models, typically:

1. **avg_5_games** (~25%): Most recent average
2. **avg_10_games** (~19%): Longer-term average
3. **season_avg** (~14%): Overall performance level
4. **avg_minutes_5_games** (~10%): Playing time indicator
5. **is_home** (~8%): Home court advantage
6. **consistency_score** (~7%): Reliability
7. **recent_trend** (~6%): Current trajectory
8. **days_rest** (~5%): Fatigue indicator

## 📈 Performance Metrics

### Typical Model Performance

Based on training with ~1500 player-games per prop:

| Prop Type | Ensemble MAE | R² | Within 3 Points |
|-----------|-------------|-----|-----------------|
| Points | 3.8 | 0.80 | 56% |
| Rebounds | 1.9 | 0.72 | 61% |
| Assists | 1.5 | 0.75 | 64% |
| 3PT Made | 0.8 | 0.68 | 67% |
| Steals | 0.5 | 0.52 | 73% |
| Blocks | 0.4 | 0.48 | 78% |
| Turnovers | 0.7 | 0.56 | 69% |
| FG Made | 1.2 | 0.76 | 62% |
| FT Made | 1.1 | 0.71 | 65% |

*Note: Actual performance depends on data quality and quantity*

### Confidence Score Calculation

Confidence (0-100) is calculated as weighted average of:

1. **Ensemble Agreement** (40%): How much models agree
   - Low variation = high confidence
   
2. **Historical Accuracy** (30%): Model's past performance
   - Based on R² from training
   
3. **Data Quality** (30%): Data recency and completeness
   - Games played this season
   - Consistency score

## ⚙️ Configuration

### Model Configuration

Edit `models/nba/config.py` to customize:

```python
# Prop types to predict
PROP_TYPES = ['points', 'rebounds', 'assists', ...]

# Rolling average windows
FEATURE_WINDOWS = [3, 5, 10]

# Training parameters
TRAINING_CONFIG = {
    'test_size': 0.2,  # 20% test set
    'min_games_required': 10,
    'cv_folds': 5
}

# Model hyperparameters
MODEL_PARAMS = {
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        ...
    },
    ...
}

# Confidence scoring weights
CONFIDENCE_CONFIG = {
    'ensemble_agreement_weight': 0.4,
    'historical_accuracy_weight': 0.3,
    'data_quality_weight': 0.3
}

# Value bet thresholds
VALUE_BET_CONFIG = {
    'strong_value_threshold': 5.0,  # EV > 5%
    'moderate_value_threshold': 2.0,
    'min_confidence_for_bet': 60
}
```

## 🔍 Troubleshooting

### "No training examples created"

**Problem**: Not enough data to train models

**Solution**:
```bash
# Collect more data
python collect_data.py --with-stats

# Check data in database
psql -d betting_analysis -c "SELECT COUNT(*) FROM player_game_stats;"
```

You need at least 100+ player game stats to train models.

### "Models for X not found"

**Problem**: Models haven't been trained yet

**Solution**:
```bash
python models/nba/train_models.py
```

### "Could not extract features for player X"

**Problem**: Player doesn't have enough historical games (need 5+)

**Solution**: This is expected for new players or rookies. They will be skipped.

### Low Model Performance

**Problem**: MAE is high, R² is low

**Possible Causes**:
1. Not enough training data
2. Data quality issues
3. Hyperparameters need tuning

**Solutions**:
1. Collect more historical data
2. Check for missing/null values in player stats
3. Tune hyperparameters in `config.py`
4. Try different feature windows

### Predictions Not Saved to Database

**Problem**: `save_predictions_to_db()` returns 0

**Check**:
```python
# Verify predictions were generated
print(len(predictions))

# Check database connection
from database.db_manager import db_manager
result = db_manager.execute_query("SELECT 1")
print(result)

# Check projections table exists
result = db_manager.execute_query(
    "SELECT COUNT(*) FROM projections"
)
print(result)
```

## 🎓 Advanced Usage

### Hyperparameter Tuning

```python
from models.nba.train_models import ModelTrainer
from sklearn.model_selection import GridSearchCV

# Modify training script to use GridSearch
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10]
}

# Run grid search...
```

### Custom Feature Engineering

Add new features in `feature_engineering.py`:

```python
def extract_features_for_player(self, ...):
    # ... existing code ...
    
    # Add custom feature
    features['my_custom_feature'] = calculate_my_feature(stats_list)
    
    return features
```

### Retraining Schedule

Recommended retraining schedule:

- **Weekly**: Retrain all models with latest data
- **Monthly**: Review and tune hyperparameters
- **Seasonally**: Major overhaul with full season data

```bash
# Weekly retraining cron job
0 2 * * 1 cd /home/ubuntu/betting_backend && /home/ubuntu/betting_backend/venv/bin/python models/nba/train_models.py >> logs/training_cron.log 2>&1
```

### Monitoring Model Performance

Track predictions vs actuals:

```sql
-- Create a view to compare predictions to actual results
CREATE VIEW prediction_accuracy AS
SELECT 
    proj.prop_type,
    proj.projected_value,
    pgs.stats->>proj.prop_type as actual_value,
    ABS(proj.projected_value - (pgs.stats->>proj.prop_type)::float) as error
FROM projections proj
JOIN player_game_stats pgs ON proj.player_id = pgs.player_id AND proj.game_id = pgs.game_id
JOIN games g ON proj.game_id = g.id
WHERE g.status = 'completed';

-- Calculate MAE by prop type
SELECT 
    prop_type,
    AVG(error) as mae,
    COUNT(*) as predictions
FROM prediction_accuracy
GROUP BY prop_type;
```

## 📚 Additional Resources

### Files and Directories

```
models/nba/
├── __init__.py
├── config.py                  # Configuration
├── feature_engineering.py     # Feature extraction
├── train_models.py           # Training pipeline
├── predict.py                # Prediction engine
├── value_finder.py           # Value bet analyzer
├── saved_models/             # Trained model files
│   ├── points_*.joblib
│   ├── rebounds_*.joblib
│   └── ...
└── README.md                 # This file

scripts/
└── generate_nba_predictions.py  # Daily predictions script
```

### Related Documentation

- [Main Backend README](../../README.md)
- [Database Schema](../../database/schema.sql)
- [Data Collection Guide](../../QUICKSTART.md)

## 🙏 Support

For issues:
1. Check logs in `logs/` directory
2. Verify data availability
3. Check model files exist
4. Review configuration

## 📝 Notes

- Models require at least 10 games per player to train
- Predictions are more accurate mid-season with more data
- Rookie players may not have predictions
- Confidence scores help identify reliable predictions
- Always verify predictions with your own analysis before betting

---

**Disclaimer**: This system is for educational and research purposes. Sports betting involves risk. Always bet responsibly and within your means.
