# Quick Start Guide

Get up and running with the NFL/NBA Betting Analysis Backend in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check PostgreSQL (need 12+)
psql --version
```

## Installation Steps

### 1. Install PostgreSQL (if not installed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

### 2. Set Up Python Environment

```bash
cd /home/ubuntu/betting_backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit if needed (defaults should work)
nano .env
```

### 4. Initialize Database

```bash
cd database
./setup_db.sh
```

If you get permission errors:
```bash
chmod +x setup_db.sh
./setup_db.sh
```

### 5. Test Data Collection

```bash
cd /home/ubuntu/betting_backend
source venv/bin/activate

# Collect teams (quick test)
python collect_data.py --teams-only
```

Expected output:
```
INFO - Collecting NBA teams...
INFO - ✓ Collected 30 NBA teams
INFO - Collecting NFL teams...
INFO - ✓ Collected 32 NFL teams
```

### 6. Run Full Collection

```bash
# This will collect teams + schedules (takes 2-5 minutes)
python collect_data.py

# Optional: Include player stats (takes 30-60 minutes)
python collect_data.py --with-stats
```

## Verify Installation

### Check Database

```bash
psql -h localhost -U betting_user -d betting_analysis

# Run these queries:
SELECT COUNT(*) FROM teams;
SELECT COUNT(*) FROM games;
SELECT * FROM upcoming_games_view LIMIT 5;

# Exit
\q
```

### Check Logs

```bash
tail -f logs/data_collection_$(date +%Y%m%d).log
```

## Set Up Daily Automation

```bash
# Edit crontab
crontab -e

# Add this line (runs at 6:00 AM daily):
0 6 * * * cd /home/ubuntu/betting_backend && /home/ubuntu/betting_backend/venv/bin/python collect_data.py >> /home/ubuntu/betting_backend/logs/cron.log 2>&1
```

## Common Issues

### PostgreSQL Not Running
```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### Permission Denied on Scripts
```bash
chmod +x database/setup_db.sh
chmod +x collect_data.py
```

### Database Connection Error
```bash
# Reset database password
sudo -u postgres psql
ALTER USER betting_user WITH PASSWORD 'betting_password';
\q
```

### API Rate Limiting
- Wait a few minutes between collection runs
- Use `--teams-only` or `--schedule-only` for faster testing
- Check `config/config.py` to adjust retry settings

## Next Steps

1. ✅ Verify data collection works
2. 📊 Explore the database schema
3. 🔄 Set up automated daily collection
4. 📈 Start building projection models using `data_processing/stats_calculator.py`
5. 🎯 Integrate with your analysis/betting system

## Quick Reference

### File Locations
- Configuration: `config/config.py`
- Database Schema: `database/schema.sql`
- Main Script: `collect_data.py`
- Logs: `logs/`
- Cache: `cache/`

### Useful Commands
```bash
# Activate environment
source venv/bin/activate

# Collect data
python collect_data.py

# Check database
psql -h localhost -U betting_user -d betting_analysis

# View logs
tail -f logs/data_collection_$(date +%Y%m%d).log

# Clear cache
rm -rf cache/espn/* cache/nba_api/*
```

## Getting Help

1. Check the comprehensive [README.md](README.md)
2. Review logs in `logs/` directory
3. Check troubleshooting section in README
4. Verify API connectivity

---

**Success!** 🎉 Your betting analysis backend is ready to collect and analyze NFL and NBA data!
