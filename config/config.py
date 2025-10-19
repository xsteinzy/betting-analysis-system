
"""
Configuration settings for the betting backend system
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'betting_analysis'),
    'user': os.getenv('DB_USER', 'betting_user'),
    'password': os.getenv('DB_PASSWORD', 'betting_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# API Configuration
ESPN_API_CONFIG = {
    'base_url': 'https://site.api.espn.com/apis/site/v2/sports',
    'retry_attempts': 3,
    'retry_delay': 2,  # seconds
    'backoff_factor': 2,
    'timeout': 30
}

NBA_API_CONFIG = {
    'retry_attempts': 3,
    'retry_delay': 2,
    'backoff_factor': 2,
    'timeout': 30
}

# Cache configuration
CACHE_DIR = BASE_DIR / 'cache'
CACHE_EXPIRY = {
    'player_data': 3600,  # 1 hour
    'game_data': 1800,    # 30 minutes
    'team_data': 86400,   # 24 hours
    'schedule_data': 3600 # 1 hour
}

# Logging configuration
LOG_DIR = BASE_DIR / 'logs'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Season configuration
CURRENT_SEASON = {
    'nba': '2024-25',
    'nfl': '2024'
}

# Data collection schedule
DATA_COLLECTION_TIME = '06:00'  # Morning update before games
