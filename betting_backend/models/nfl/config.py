

"""
Configuration for NFL ML prediction models
"""
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / 'models' / 'nfl' / 'saved_models'

# Ensure models directory exists
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Prop types to predict
PROP_TYPES = [
    'passing_yards',
    'rushing_yards',
    'receiving_yards',
    'passing_touchdowns',
    'rushing_touchdowns',
    'receiving_touchdowns',
    'receptions',
    'interceptions',
    'completions',
    'field_goals_made'
]

# Stat keys mapping for data extraction
STAT_KEYS_MAPPING = {
    'passing_yards': 'passing_yards',
    'rushing_yards': 'rushing_yards',
    'receiving_yards': 'receiving_yards',
    'passing_touchdowns': 'passing_touchdowns',
    'rushing_touchdowns': 'rushing_touchdowns',
    'receiving_touchdowns': 'receiving_touchdowns',
    'receptions': 'receptions',
    'interceptions': 'interceptions',
    'completions': 'completions',
    'field_goals_made': 'field_goals_made'
}

# Position-specific prop types
POSITION_PROP_MAPPING = {
    'QB': ['passing_yards', 'passing_touchdowns', 'interceptions', 'completions', 'rushing_yards'],
    'RB': ['rushing_yards', 'rushing_touchdowns', 'receiving_yards', 'receptions', 'receiving_touchdowns'],
    'WR': ['receiving_yards', 'receptions', 'receiving_touchdowns'],
    'TE': ['receiving_yards', 'receptions', 'receiving_touchdowns'],
    'K': ['field_goals_made']
}

# Feature windows for rolling averages
FEATURE_WINDOWS = [3, 5, 10]

# Model hyperparameters (same as NBA for consistency)
MODEL_PARAMS = {
    'linear_regression': {
        'fit_intercept': True,
        'normalize': False
    },
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1
    },
    'gradient_boosting': {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 5,
        'min_child_weight': 3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'n_jobs': -1
    }
}

# Training parameters
TRAINING_CONFIG = {
    'test_size': 0.2,
    'min_games_required': 5,  # NFL has fewer games per season (17 games)
    'cv_folds': 5,
    'random_state': 42
}

# Confidence score parameters
CONFIDENCE_CONFIG = {
    'ensemble_agreement_weight': 0.4,  # Weight for model agreement
    'historical_accuracy_weight': 0.3,  # Weight for historical accuracy
    'data_quality_weight': 0.3,  # Weight for data recency/completeness
    'min_confidence': 0,
    'max_confidence': 100
}

# Value bet thresholds
VALUE_BET_CONFIG = {
    'strong_value_threshold': 5.0,  # EV > 5%
    'moderate_value_threshold': 2.0,  # EV 2-5%
    'slight_value_threshold': 0.0,  # EV 0-2%
    'min_confidence_for_bet': 60,  # Minimum confidence to recommend bet
    'min_edge_for_recommendation': 5.0  # Minimum edge (prediction - line) for recommendation (higher for NFL)
}

# Model file paths
MODEL_FILES = {
    prop_type: {
        'linear_regression': MODELS_DIR / f'{prop_type}_linear_regression.joblib',
        'random_forest': MODELS_DIR / f'{prop_type}_random_forest.joblib',
        'gradient_boosting': MODELS_DIR / f'{prop_type}_gradient_boosting.joblib',
        'scaler': MODELS_DIR / f'{prop_type}_scaler.joblib',
        'metadata': MODELS_DIR / f'{prop_type}_metadata.json'
    }
    for prop_type in PROP_TYPES
}

# Feature columns (will be dynamically generated)
FEATURE_COLUMNS = [
    # Rolling averages
    'avg_3_games',
    'avg_5_games',
    'avg_10_games',
    
    # Home/away splits
    'home_avg',
    'away_avg',
    'is_home',
    
    # Rest and recent form
    'days_rest',
    'games_played_last_4_weeks',
    'recent_trend',  # Slope of recent performance
    
    # Consistency metrics
    'consistency_score',
    'std_dev_last_5',
    
    # Opponent metrics (if available)
    'opponent_defensive_rating',
    'matchup_history_avg',
    
    # Season metrics
    'season_avg',
    'games_played_this_season',
    
    # Snaps/Usage (important predictor for NFL)
    'avg_snaps_3_games',
    'avg_snaps_5_games'
]

# Logging
MODEL_VERSION = '1.0.0'

