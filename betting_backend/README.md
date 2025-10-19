# NFL and NBA Betting Analysis Backend

A comprehensive backend data infrastructure for collecting, storing, and analyzing NFL and NBA data for betting analysis. This system provides daily data collection, historical data storage, and statistical processing utilities.

## 🚀 Features

- **Multi-Sport Support**: NFL and NBA data collection and analysis
- **Robust API Integration**: 
  - ESPN Hidden API with retry logic and exponential backoff
  - NBA API using the official `nba_api` Python library
- **PostgreSQL Database**: Optimized schema with proper indexing and foreign keys
- **Data Processing Utilities**: 
  - Rolling averages (3, 5, 10 games)
  - Home/away performance splits
  - Opponent defensive rankings
  - Days rest calculations
  - Trend analysis and outlier detection
- **Caching System**: File-based caching to minimize API calls
- **Error Handling**: Comprehensive error handling and logging
- **Daily Updates**: Automated data collection for morning updates before games

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [PostgreSQL Setup](#postgresql-setup)
  - [Python Environment](#python-environment)
  - [Database Initialization](#database-initialization)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Data Collection](#data-collection)
  - [Accessing Data](#accessing-data)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [API Rate Limits](#api-rate-limits)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🖥️ System Requirements

- Python 3.8 or higher
- PostgreSQL 12 or higher
- 2GB RAM minimum
- 10GB disk space (for data and caching)
- Internet connection for API access

## 🔧 Installation

### PostgreSQL Setup

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

#### macOS

```bash
# Install PostgreSQL using Homebrew
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15
```

#### Windows

Download and install PostgreSQL from [official website](https://www.postgresql.org/download/windows/)

### Python Environment

```bash
# Navigate to project directory
cd /home/ubuntu/betting_backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Initialization

```bash
# Navigate to database directory
cd database

# Run setup script (will create database, user, and schema)
./setup_db.sh

# If you encounter permission issues, run:
chmod +x setup_db.sh
```

**Manual Database Setup** (if script fails):

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In psql prompt:
CREATE USER betting_user WITH PASSWORD 'betting_password';
CREATE DATABASE betting_analysis OWNER betting_user;
GRANT ALL PRIVILEGES ON DATABASE betting_analysis TO betting_user;
\q

# Run schema creation
PGPASSWORD=betting_password psql -h localhost -U betting_user -d betting_analysis -f schema.sql
```

## ⚙️ Configuration

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Database Configuration
DB_NAME=betting_analysis
DB_USER=betting_user
DB_PASSWORD=betting_password
DB_HOST=localhost
DB_PORT=5432

# Logging
LOG_LEVEL=INFO
```

### Configuration File

Edit `config/config.py` to customize:
- API retry settings
- Cache expiry times
- Current season
- Data collection schedule

## 📊 Usage

### Data Collection

#### Daily Collection (Recommended)

Run this every morning before games start:

```bash
# Activate virtual environment
source venv/bin/activate

# Run daily collection
python collect_data.py
```

#### With Player Statistics

Collecting player statistics is time-consuming (can take 30-60 minutes):

```bash
python collect_data.py --with-stats
```

#### Teams Only

```bash
python collect_data.py --teams-only
```

#### Schedule Only

```bash
python collect_data.py --schedule-only
```

### Automated Daily Collection

Set up a cron job for daily collection:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 6:00 AM daily)
0 6 * * * cd /home/ubuntu/betting_backend && /home/ubuntu/betting_backend/venv/bin/python collect_data.py >> /home/ubuntu/betting_backend/logs/cron.log 2>&1
```

### Accessing Data

#### Using Python

```python
from database.db_manager import db_manager

# Get upcoming games
upcoming_nba = db_manager.get_upcoming_games('NBA', days_ahead=7)
upcoming_nfl = db_manager.get_upcoming_games('NFL', days_ahead=7)

# Get player stats
player = db_manager.get_player_by_external_id('2544', 'NBA')  # LeBron James
recent_stats = db_manager.get_player_recent_stats(player['id'], limit=10)

# Close connection when done
db_manager.close()
```

#### Using SQL

```bash
# Connect to database
psql -h localhost -U betting_user -d betting_analysis

# Example queries
SELECT * FROM upcoming_games_view WHERE sport = 'NBA';
SELECT * FROM player_stats_view WHERE player_name LIKE '%LeBron%' LIMIT 10;
```

### Data Processing

```python
from data_processing.stats_calculator import StatsCalculator, OpponentAnalyzer, TrendAnalyzer
from database.db_manager import db_manager

# Get player stats
player_id = 123
stats_list = db_manager.get_player_recent_stats(player_id, limit=20)

# Calculate rolling averages
rolling_avgs = StatsCalculator.calculate_multiple_rolling_averages(
    stats_list,
    stat_keys=['points', 'rebounds', 'assists'],
    windows=[3, 5, 10]
)

# Calculate home/away splits
splits = StatsCalculator.calculate_home_away_splits(
    stats_list,
    stat_keys=['points', 'rebounds', 'assists']
)

# Analyze trends
trend = TrendAnalyzer.calculate_trend(stats_list, 'points', window=10)
```

## 🗄️ Database Schema

### Tables

1. **teams**: Team information (NFL and NBA)
2. **players**: Player information with team associations
3. **games**: Game schedules and results
4. **player_game_stats**: Comprehensive player statistics in JSONB format
5. **projections**: Model-generated projections for player props
6. **bets**: Betting history and outcomes

### Key Features

- **JSONB Storage**: Flexible stats storage supporting all metrics
- **Foreign Keys**: Proper relational integrity
- **Indexes**: Optimized for common queries
- **Views**: Pre-built views for common data access patterns
- **Triggers**: Automatic timestamp updates

### Stats Storage Format

#### NBA Stats (JSONB)
```json
{
  "minutes": 35.5,
  "points": 28,
  "rebounds": 8,
  "assists": 7,
  "steals": 2,
  "blocks": 1,
  "turnovers": 3,
  "fg_made": 10,
  "fg_attempts": 20,
  "fg_percentage": 0.500,
  "three_pt_made": 3,
  "three_pt_attempts": 8,
  "three_pt_percentage": 0.375,
  "ft_made": 5,
  "ft_attempts": 6,
  "ft_percentage": 0.833
}
```

#### NFL Stats (JSONB)
```json
{
  "passing_yards": 325,
  "rushing_yards": 45,
  "receiving_yards": 0,
  "touchdowns": 3,
  "receptions": 0,
  "completions": 25,
  "attempts": 35,
  "interceptions": 1
}
```

## 📁 Project Structure

```
betting_backend/
├── cache/                      # API response cache
│   ├── espn/                   # ESPN API cache
│   └── nba_api/                # NBA API cache
├── config/                     # Configuration files
│   ├── __init__.py
│   └── config.py               # Main configuration
├── data_collection/            # Data collection modules
│   ├── __init__.py
│   ├── espn_api.py             # ESPN API client
│   └── nba_api_client.py       # NBA API client
├── data_processing/            # Data processing utilities
│   ├── __init__.py
│   └── stats_calculator.py     # Statistical calculations
├── database/                   # Database management
│   ├── __init__.py
│   ├── schema.sql              # Database schema
│   ├── setup_db.sh             # Database setup script
│   └── db_manager.py           # Database operations
├── logs/                       # Application logs
├── utils/                      # Utility modules
│   ├── __init__.py
│   └── logger.py               # Logging configuration
├── collect_data.py             # Main data collection script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## ⚠️ API Rate Limits

### ESPN Hidden API
- No official rate limit documentation
- Implemented retry logic with exponential backoff
- 0.5-1 second delay between requests recommended
- Caching used to minimize requests

### NBA API (nba_api)
- ~100 requests per minute limit
- 0.6 second delay between requests enforced
- Aggressive caching recommended
- Use sparingly during peak hours

### Best Practices
- Run data collection during off-peak hours (early morning)
- Use caching aggressively
- Only collect data you need
- Monitor logs for rate limit errors

## 🔍 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if you can connect
psql -h localhost -U betting_user -d betting_analysis

# Reset password if needed
sudo -u postgres psql
ALTER USER betting_user WITH PASSWORD 'new_password';
```

### API Errors

- **Rate Limiting**: Increase retry delays in `config/config.py`
- **Timeout**: Increase timeout values in configuration
- **No Data**: Check if season/date parameters are correct

### Cache Issues

```bash
# Clear cache if data seems stale
rm -rf cache/espn/*
rm -rf cache/nba_api/*
```

### Permission Issues

```bash
# Fix directory permissions
chmod -R 755 /home/ubuntu/betting_backend
chmod +x database/setup_db.sh
chmod +x collect_data.py
```

## 📝 Logging

Logs are stored in `logs/` directory:
- `data_collection_YYYYMMDD.log`: Data collection logs
- Rotated daily with 5-day retention
- Set `LOG_LEVEL` in `.env` to control verbosity (DEBUG, INFO, WARNING, ERROR)

View live logs:
```bash
tail -f logs/data_collection_$(date +%Y%m%d).log
```

## 🔄 Data Update Frequency

- **Teams**: Weekly or when roster changes occur
- **Schedules**: Daily for next 7 days (NBA) / 4 weeks (NFL)
- **Player Stats**: After games complete (next morning update)
- **Projections**: As needed before making bets

## 🎯 Next Steps

After setting up the backend:

1. **Verify Data Collection**: Run initial collection and verify data in database
2. **Set Up Cron Jobs**: Automate daily data collection
3. **Build Projection Models**: Use data processing utilities to create models
4. **Integrate with Frontend**: Connect to analysis/betting interface
5. **Backfill Historical Data**: Modify scripts to collect historical seasons

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational and personal use only. Ensure compliance with:
- ESPN API Terms of Service
- NBA.com Terms of Service
- Applicable gambling laws in your jurisdiction

## 🆘 Support

For issues and questions:
1. Check logs in `logs/` directory
2. Review troubleshooting section
3. Check API status (ESPN, NBA)
4. Verify database connectivity

## 🙏 Acknowledgments

- ESPN for providing accessible sports data
- NBA API Python library maintainers
- PostgreSQL community
- Python community

---

**Note**: This system is designed for the 2024-2025 NBA season and 2024 NFL season. Update `CURRENT_SEASON` in `config/config.py` for future seasons.

**Disclaimer**: This tool is for research and analysis purposes only. Always bet responsibly and within your means.
