# NFL ML System Quick Start Guide

Get started with the NFL machine learning prediction system in 5 minutes.

## Prerequisites

- Betting backend installed and configured
- PostgreSQL database running
- Python virtual environment activated
- Basic NFL player data collected

## Step 1: Install Dependencies (1 minute)

```bash
cd /home/ubuntu/betting_backend
source venv/bin/activate
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import sklearn, xgboost; print('✓ ML libraries ready')"
```

## Step 2: Collect NFL Data (10-30 minutes)

```bash
# Collect current season data
python collect_data.py --sport NFL

# Check data
psql -d betting_analysis -c "SELECT COUNT(*) FROM player_game_stats WHERE player_id IN (SELECT id FROM players WHERE sport='NFL');"
```

You need at least 50 player game stats to train models.

## Step 3: Train Models (5-15 minutes)

Train all 10 prop type models:

```bash
python models/nfl/train_models.py
```

Or train just one for testing:

```bash
python models/nfl/train_models.py --test
```

What happens during training:
- Loads historical NFL player stats
- Engineers 18 features per prediction
- Trains 3 models per prop type (Linear, Random Forest, XGBoost)
- Evaluates with cross-validation
- Saves models to disk

Expected output:
```
Training models for passing_yards
Train size: 250, Test size: 62

ENSEMBLE (Average):
  MAE: 26.8
  R²: 0.78
  Within 20 yards: 57.1%

✓ Models saved
```

## Step 4: Generate Predictions (30 seconds)

Generate predictions for this week's games:

```bash
python scripts/generate_nfl_predictions.py
```

Or use the unified multi-sport script:

```bash
python scripts/generate_predictions.py --sport nfl
```

Expected output:
```
Generating NFL Predictions for Week 7

Found 14 games in Week 7
Generated 450 predictions

By Prop Type:
  passing_yards: 32 predictions (avg confidence: 72.4%)
  rushing_yards: 64 predictions (avg confidence: 68.1%)
  receiving_yards: 96 predictions (avg confidence: 70.5%)
  ...

✓ Saved 450 predictions to database
```

## Step 5: View Predictions (1 minute)

### In Database

```bash
psql -d betting_analysis
```

```sql
-- View high confidence predictions
SELECT 
    p.name as player,
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
  AND proj.confidence >= 75
ORDER BY proj.confidence DESC;
```

### In Python

```python
from models.nfl.predict import NFLPredictor

predictor = NFLPredictor()
predictions = predictor.predict_week_games()

# Show QB passing yards predictions
for pred in predictions:
    if pred['prop_type'] == 'passing_yards' and pred['position'] == 'QB':
        print(f"{pred['player_name']}: {pred['predicted_value']} yards "
              f"(confidence: {pred['confidence_score']}%)")
```

## Common Commands

```bash
# Train models
python models/nfl/train_models.py

# Generate predictions for current week
python scripts/generate_nfl_predictions.py

# Generate predictions for specific week
python scripts/generate_nfl_predictions.py --week 7

# Retrain models and generate predictions
python scripts/generate_nfl_predictions.py --retrain

# Generate for both NBA and NFL
python scripts/generate_predictions.py --sport both

# View examples
python models/nfl/example_usage.py

# Test system
python scripts/test_nfl_system.py
```

## Position-Specific Props

The system automatically predicts only relevant props for each position:

- **QB**: Passing yards, passing TDs, interceptions, completions, rushing yards
- **RB**: Rushing yards, rushing TDs, receiving yards, receptions, receiving TDs
- **WR/TE**: Receiving yards, receptions, receiving TDs
- **K**: Field goals made

## Next Steps

1. **Set up automated weekly runs**:
   ```bash
   crontab -e
   # Add: 0 8 * * 2 cd /home/ubuntu/betting_backend && /home/ubuntu/betting_backend/venv/bin/python scripts/generate_nfl_predictions.py
   ```

2. **Compare to betting lines**: Use the value finder to identify value bets

3. **Track performance**: Monitor prediction accuracy over time

4. **Retrain weekly**: Update models with latest data each week

## Troubleshooting

**No data**: Run `python collect_data.py --sport NFL`

**No models**: Run `python models/nfl/train_models.py`

**No games**: Check if it's an NFL week (season runs Sept-Jan)

**Low confidence**: Need more historical data - collect multiple seasons

## NFL vs NBA Differences

| Feature | NFL | NBA |
|---------|-----|-----|
| Games per season | 17 | 82 |
| Schedule | Weekly | Daily |
| Min games for training | 5 | 10 |
| Prop types | 10 | 10 |
| Positions | QB, RB, WR, TE, K | All similar |
| Season | Sep-Jan | Oct-Apr |

## Performance Expectations

With sufficient data:
- Passing yards: ±28 yards MAE
- Rushing yards: ±18 yards MAE
- Receiving yards: ±15 yards MAE
- Touchdowns: ±0.7 TDs MAE
- Confidence scores: 60-80% typical range

## Getting Help

1. Check [Full NFL README](models/nfl/README.md)
2. Review [Example Usage](models/nfl/example_usage.py)
3. Read [ML System Summary](ML_SYSTEM_SUMMARY.md)
4. Check logs in `logs/` directory

---

**Ready to go!** Start generating NFL predictions and identifying value bets.
