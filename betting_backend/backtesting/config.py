
"""
Backtesting Configuration
Defines all parameters for backtesting betting strategies
"""

# Entry Type Payouts (multipliers)
ENTRY_PAYOUTS = {
    2: 3.0,   # 2-pick entries pay 3x
    3: 6.0,   # 3-pick entries pay 6x
    4: 10.0,  # 4-pick entries pay 10x
    5: 20.0   # 5-pick entries pay 20x
}

# Confidence Thresholds (%)
CONFIDENCE_THRESHOLDS = [60, 65, 70, 75, 80, 85, 90]

# Expected Value (EV) Thresholds (%)
EV_THRESHOLDS = [0, 5, 10, 15, 20]

# Bankroll Management Strategies
BANKROLL_STRATEGIES = {
    'flat': {
        'description': 'Fixed bet size regardless of bankroll',
        'amounts': [10, 25, 50, 100]  # Fixed amounts in dollars
    },
    'percentage': {
        'description': 'Bet a fixed percentage of current bankroll',
        'percentages': [1, 2, 3, 5]  # Percentage of bankroll
    },
    'kelly': {
        'description': 'Kelly Criterion - optimal bet sizing based on edge',
        'kelly_fraction': [0.25, 0.5, 1.0]  # Fraction of Kelly to use (conservative to aggressive)
    }
}

# Betting Strategies
BETTING_STRATEGIES = {
    'confidence_based': {
        'name': 'Confidence-Based',
        'description': 'Only bet when model confidence exceeds threshold',
        'parameters': ['confidence_threshold']
    },
    'value_based': {
        'name': 'Value-Based',
        'description': 'Only bet when expected value exceeds threshold',
        'parameters': ['ev_threshold']
    },
    'prop_specific': {
        'name': 'Prop-Specific',
        'description': 'Focus on specific prop types',
        'parameters': ['prop_types']
    },
    'sport_specific': {
        'name': 'Sport-Specific',
        'description': 'Focus on specific sports',
        'parameters': ['sports']
    },
    'entry_size_specific': {
        'name': 'Entry-Size-Specific',
        'description': 'Focus on specific entry sizes',
        'parameters': ['entry_sizes']
    },
    'composite': {
        'name': 'Composite Strategy',
        'description': 'Combination of multiple filters',
        'parameters': ['confidence_threshold', 'ev_threshold', 'prop_types', 'entry_sizes']
    }
}

# Prop Types by Sport
PROP_TYPES = {
    'NBA': [
        'points',
        'rebounds',
        'assists',
        'steals',
        'blocks',
        'three_pointers_made',
        'points_rebounds_assists',
        'points_rebounds',
        'points_assists',
        'rebounds_assists'
    ],
    'NFL': [
        'passing_yards',
        'passing_touchdowns',
        'rushing_yards',
        'rushing_touchdowns',
        'receiving_yards',
        'receiving_touchdowns',
        'receptions',
        'completions',
        'pass_attempts',
        'interceptions'
    ]
}

# Performance Metrics to Track
PERFORMANCE_METRICS = [
    'total_bets',
    'wins',
    'losses',
    'win_rate',
    'total_profit',
    'roi',
    'max_drawdown',
    'sharpe_ratio',
    'avg_bet_size',
    'total_staked',
    'profit_factor',
    'longest_win_streak',
    'longest_loss_streak'
]

# Default Backtesting Parameters
DEFAULT_BACKTEST_PARAMS = {
    'starting_bankroll': 1000.0,
    'bet_size': 50.0,
    'bankroll_strategy': 'flat',
    'confidence_threshold': 70,
    'ev_threshold': 5,
    'entry_sizes': [2, 3, 4, 5],  # All entry sizes
    'sports': ['NBA', 'NFL'],
    'min_games_history': 5,  # Minimum games of history required for a player
    'risk_free_rate': 0.02  # Annual risk-free rate for Sharpe ratio calculation
}

# Date Ranges for Backtesting
DATE_RANGES = {
    'last_week': 7,
    'last_month': 30,
    'last_quarter': 90,
    'last_season': 180,
    'custom': None  # User-defined
}

# Database Configuration
BACKTEST_RESULTS_TABLE = 'backtest_results'

# Logging Configuration
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'backtesting.log'
}

# Chart Data Configuration
CHART_CONFIG = {
    'cumulative_pl_points': 100,  # Number of data points for cumulative P&L chart
    'win_rate_window': 20,  # Moving window for win rate chart
    'performance_periods': ['weekly', 'monthly']
}

# Insights Configuration
INSIGHTS_CONFIG = {
    'min_sample_size': 30,  # Minimum bets required for valid insights
    'significance_threshold': 0.05,  # Statistical significance threshold
    'top_insights_count': 10,  # Number of top insights to generate
    'comparison_threshold': 5.0  # Minimum % difference for comparisons
}

# Multi-threading Configuration
PARALLEL_CONFIG = {
    'max_workers': 4,  # Number of parallel workers for backtesting
    'chunk_size': 100  # Number of bets to process per chunk
}

