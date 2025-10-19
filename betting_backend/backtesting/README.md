# Betting Strategy Backtesting Engine

A comprehensive backtesting system for evaluating betting strategies on historical sports prediction data. Test different strategies, analyze performance across multiple dimensions, and generate actionable insights to optimize your betting approach.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Strategies](#available-strategies)
- [Configuration](#configuration)
- [Running Backtests](#running-backtests)
- [API Integration](#api-integration)
- [Automation](#automation)
- [Understanding Results](#understanding-results)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The backtesting engine simulates betting strategies on historical prediction data to evaluate their performance without risking real money. It helps answer questions like:

- Which entry size (2-pick, 3-pick, 4-pick, 5-pick) is most profitable?
- Should I focus on NBA or NFL props?
- What confidence threshold should I use?
- Which prop types have the highest win rate?
- How much should I bet per entry?

## Features

### Strategy Simulation
- **Confidence-Based**: Bet only when model confidence exceeds threshold
- **Value-Based**: Bet only when expected value exceeds threshold
- **Prop-Specific**: Focus on specific prop types (e.g., points, assists)
- **Sport-Specific**: NBA only, NFL only, or both
- **Composite**: Combine multiple filters for optimal results

### Bankroll Management
- **Flat Betting**: Fixed bet size regardless of bankroll
- **Percentage**: Bet a fixed percentage of current bankroll
- **Kelly Criterion**: Optimal bet sizing based on edge

### Performance Analysis
- Win rate by entry size, prop type, sport, confidence level
- ROI, profit factor, Sharpe ratio, max drawdown
- Best prop combinations for parlays
- Risk-adjusted returns
- Time series analysis

### Actionable Insights
- Automatically generated insights from backtest results
- Identifies strengths and weaknesses
- Provides specific recommendations
- Highlights optimal strategies

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database with schema installed
- Historical prediction and game data

### Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Database Migration**
```bash
psql -U betting_user -d betting_analysis -f database/migrations/add_backtest_results.sql
```

3. **Verify Installation**
```bash
python backtesting/run_backtest.py --help
```

## Quick Start

Run your first backtest in 3 steps:

### 1. Basic Confidence-Based Strategy
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy confidence_based \
  --confidence-threshold 75 \
  --save
```

### 2. NBA-Only High Confidence Strategy
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy confidence_based \
  --sport NBA \
  --confidence-threshold 80 \
  --entry-sizes 2 3 \
  --save
```

### 3. Composite Strategy with Multiple Filters
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy composite \
  --confidence-threshold 75 \
  --ev-threshold 5 \
  --entry-sizes 2 3 4 5 \
  --bankroll 2000 \
  --bet-size 100 \
  --save
```

## Available Strategies

### 1. Confidence-Based Strategy
Bets only when model confidence exceeds a threshold.

**Parameters:**
- `--confidence-threshold`: Minimum confidence (60-100)

**Use When:**
- You trust your model's confidence scores
- You want simple, easy-to-understand filters
- You prefer conservative betting

**Example:**
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy confidence_based \
  --confidence-threshold 75
```

### 2. Value-Based Strategy
Bets only when expected value exceeds a threshold.

**Parameters:**
- `--ev-threshold`: Minimum EV percentage (0-20)

**Use When:**
- You want to focus on high-value bets
- You're willing to bet less frequently for higher quality
- You have accurate EV calculations

**Example:**
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy value_based \
  --ev-threshold 10
```

### 3. Prop-Specific Strategy
Focuses on specific prop types that historically perform well.

**Parameters:**
- `--props`: List of prop types (e.g., points, assists, rebounds)

**Use When:**
- Certain props have shown strong historical performance
- You want to specialize in specific bet types
- You have expertise in particular stats

**Example:**
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy prop_specific \
  --props points assists \
  --sport NBA
```

### 4. Composite Strategy
Combines multiple filters for refined bet selection.

**Parameters:**
- `--confidence-threshold`: Minimum confidence
- `--ev-threshold`: Minimum EV
- `--props`: Specific prop types (optional)
- `--entry-sizes`: Specific entry sizes

**Use When:**
- You want the most refined bet selection
- You're willing to sacrifice bet volume for quality
- You want to test multiple filters together

**Example:**
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 \
  --end-date 2024-10-19 \
  --strategy composite \
  --confidence-threshold 75 \
  --ev-threshold 5 \
  --entry-sizes 2 3
```

## Configuration

### Entry Type Payouts
```python
2-pick entries: 3x payout
3-pick entries: 6x payout
4-pick entries: 10x payout
5-pick entries: 20x payout
```

### Recommended Confidence Thresholds
- **Conservative**: 80%+ (fewer bets, higher quality)
- **Moderate**: 70-80% (balanced approach)
- **Aggressive**: 60-70% (more bets, lower quality)

### Bankroll Strategies

#### Flat Betting
```bash
--bankroll 1000 --bet-size 50 --bankroll-strategy flat
```
Pros: Simple, consistent
Cons: Doesn't adapt to performance

#### Percentage Betting
```bash
--bankroll 1000 --bet-size 5 --bankroll-strategy percentage
```
Pros: Scales with bankroll
Cons: Can be volatile

#### Kelly Criterion
```bash
--bankroll 1000 --bet-size 0.5 --bankroll-strategy kelly
```
Pros: Mathematically optimal
Cons: Can be aggressive

## Running Backtests

### Command-Line Interface

Basic syntax:
```bash
python backtesting/run_backtest.py [OPTIONS]
```

### Required Arguments
- `--start-date`: Start date (YYYY-MM-DD)
- `--end-date`: End date (YYYY-MM-DD)
- `--strategy`: Strategy name (confidence_based, value_based, prop_specific, composite)

### Optional Arguments
- `--sport`: NBA, NFL, or both (default: both)
- `--confidence-threshold`: Minimum confidence (default: 70)
- `--ev-threshold`: Minimum EV (default: 5)
- `--props`: Specific prop types
- `--entry-sizes`: Entry sizes to test (default: 2 3 4 5)
- `--bankroll`: Starting bankroll (default: 1000)
- `--bet-size`: Bet size or percentage (default: 50)
- `--bankroll-strategy`: flat, percentage, or kelly (default: flat)
- `--save`: Save results to database
- `--output`: Save results to JSON file
- `--verbose`: Show detailed output

### Example Commands

**Test last month's data:**
```bash
python backtesting/run_backtest.py \
  --start-date $(date -d '30 days ago' +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --strategy confidence_based \
  --confidence-threshold 75 \
  --save
```

**Compare NBA vs NFL:**
```bash
# NBA only
python backtesting/run_backtest.py \
  --start-date 2024-09-01 --end-date 2024-10-19 \
  --strategy confidence_based --sport NBA --save

# NFL only
python backtesting/run_backtest.py \
  --start-date 2024-09-01 --end-date 2024-10-19 \
  --strategy confidence_based --sport NFL --save
```

**Save results to file:**
```bash
python backtesting/run_backtest.py \
  --start-date 2024-09-01 --end-date 2024-10-19 \
  --strategy composite \
  --confidence-threshold 80 --ev-threshold 10 \
  --output results.json
```

## API Integration

The backtesting engine provides API functions for dashboard integration.

### Python API

```python
from backtesting.api import BacktestingAPI

api = BacktestingAPI()

# Get strategy performance
strategies = api.get_strategy_performance(sport='NBA', limit=10)

# Get entry size analysis
entry_analysis = api.get_entry_size_analysis()

# Get prop type performance
prop_performance = api.get_prop_type_performance()

# Get sport comparison
comparison = api.get_sport_comparison()

# Get key insights
insights = api.get_key_insights(limit=5)

# Get chart data
chart_data = api.get_historical_chart_data(chart_type='cumulative_pl')

# Get overall summary
summary = api.get_backtest_summary()

# Get best strategies
best = api.get_best_strategies(metric='roi', limit=5)
```

### Convenience Functions

```python
from backtesting.api import (
    get_strategy_performance,
    get_key_insights,
    get_sport_comparison
)

# Direct function calls without instantiating API
strategies = get_strategy_performance(sport='NBA')
insights = get_key_insights(limit=5)
comparison = get_sport_comparison()
```

## Automation

### Weekly Backtesting Script

Run automated backtests on recent data:

```bash
python scripts/run_weekly_backtest.py
```

This script:
- Tests multiple strategies on last 30 days
- Tests both NBA and NFL separately
- Saves all results to database
- Generates summary report
- Identifies best performers

### Cron Job Setup

Run weekly backtests automatically:

```bash
# Edit crontab
crontab -e

# Add line to run every Monday at 6 AM
0 6 * * 1 cd /home/ubuntu/betting_backend && python scripts/run_weekly_backtest.py >> logs/weekly_backtest.log 2>&1
```

## Understanding Results

### Performance Metrics

**Win Rate**: Percentage of winning bets
- Good: 55%+
- Excellent: 60%+

**ROI (Return on Investment)**: Profit as percentage of total staked
- Good: 5%+
- Excellent: 15%+

**Sharpe Ratio**: Risk-adjusted returns
- Good: 1.0+
- Excellent: 2.0+

**Max Drawdown**: Largest peak-to-trough decline
- Good: <20%
- Concerning: >30%

**Profit Factor**: Gross profit / Gross loss
- Good: 1.5+
- Excellent: 2.0+

### Reading Insights

Insights are categorized by type:
- ✅ **Success**: Positive findings
- ⚠️ **Warning**: Areas of concern
- ℹ️ **Info**: Neutral observations

Insights are prioritized:
- **High**: Critical findings requiring action
- **Medium**: Important but not urgent
- **Low**: Nice-to-know information

### Example Output

```
📊 Performance Summary:
  Total Bets: 150
  Wins: 85 | Losses: 65
  Win Rate: 56.67%
  Total Profit: $1,245.50
  ROI: 16.61%
  Max Drawdown: 12.34%
  Sharpe Ratio: 1.85

💡 Key Insights:
  1. ✅ Strong Win Rate
     Your strategy achieved a 56.67% win rate, which is excellent for sports betting.
  
  2. ✅ 3-Pick Entries Perform Best
     3-pick entries have the highest ROI at 22.5% with a 60% win rate.
  
  3. ℹ️ NBA Outperforms NFL
     NBA props have 8.5% higher win rate than NFL (58% vs 49.5%).
```

## Best Practices

### 1. Start with Sufficient Data
- Minimum 30 days of historical data
- At least 50-100 bets for statistical significance
- Test across different market conditions

### 2. Test Multiple Strategies
- Don't rely on a single strategy
- Compare different approaches
- Combine best elements from each

### 3. Use Conservative Bankroll Management
- Start with flat betting
- Don't bet more than 5% per entry
- Maintain proper bankroll buffer

### 4. Validate Before Live Betting
- Paper trade strategy first
- Start with minimal stakes
- Gradually scale up

### 5. Monitor and Adjust
- Run weekly backtests
- Track performance over time
- Adjust filters as needed

### 6. Beware of Overfitting
- Don't over-optimize on past data
- Test on out-of-sample data
- Keep strategies simple and robust

## Examples

### Example 1: Find Optimal Confidence Threshold

Test different confidence levels:

```bash
for threshold in 60 65 70 75 80; do
  python backtesting/run_backtest.py \
    --start-date 2024-09-01 --end-date 2024-10-19 \
    --strategy confidence_based \
    --confidence-threshold $threshold \
    --save
done
```

### Example 2: Compare Entry Sizes

Test each entry size separately:

```bash
for size in 2 3 4 5; do
  python backtesting/run_backtest.py \
    --start-date 2024-09-01 --end-date 2024-10-19 \
    --strategy confidence_based \
    --entry-sizes $size \
    --save
done
```

### Example 3: Test Prop Combinations

```bash
# Points only
python backtesting/run_backtest.py \
  --start-date 2024-09-01 --end-date 2024-10-19 \
  --strategy prop_specific --props points --sport NBA --save

# Points + Assists
python backtesting/run_backtest.py \
  --start-date 2024-09-01 --end-date 2024-10-19 \
  --strategy prop_specific --props points assists --sport NBA --save

# Points + Rebounds
python backtesting/run_backtest.py \
  --start-date 2024-09-01 --end-date 2024-10-19 \
  --strategy prop_specific --props points rebounds --sport NBA --save
```

## Troubleshooting

### No predictions found
**Issue**: No historical predictions in database for date range

**Solutions:**
- Verify date range has completed games
- Check that predictions were generated for those dates
- Run prediction generation scripts if needed

### Database connection errors
**Issue**: Cannot connect to PostgreSQL

**Solutions:**
- Check database credentials in config
- Ensure PostgreSQL is running
- Verify database exists and schema is installed

### Low number of bets generated
**Issue**: Backtest produces very few bets

**Solutions:**
- Lower confidence threshold
- Expand date range
- Include both sports
- Remove restrictive filters

### Negative ROI
**Issue**: Strategy shows losses

**Solutions:**
- Increase confidence threshold
- Test different entry sizes
- Focus on best-performing props
- Use composite strategy with multiple filters

### Memory errors on large datasets
**Issue**: Script crashes with large date ranges

**Solutions:**
- Break into smaller date ranges
- Reduce entry size combinations
- Focus on specific sport

## Support

For issues or questions:
- Check logs in `logs/backtesting.log`
- Review database for saved results
- Consult API documentation

## Future Enhancements

Planned features:
- Multi-threaded backtesting for speed
- More sophisticated EV calculations
- Player-specific performance tracking
- Market timing optimization
- Advanced bankroll strategies
- Real-time strategy monitoring

## License

Part of the betting_backend system. Internal use only.
