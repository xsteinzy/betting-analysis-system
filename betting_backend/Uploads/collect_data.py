
#!/usr/bin/env python3
"""
Daily data collection script for NFL and NBA betting analysis system

This script orchestrates the collection of:
- Team rosters
- Game schedules
- Player game statistics
- Current season data

Run this script daily (preferably in the morning) to update the database
with the latest data before games start.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from database.db_manager import db_manager
from data_collection.espn_api import espn_client
from data_collection.nba_api_client import nba_client
from config import CURRENT_SEASON

logger = setup_logger('data_collection')


class DataCollector:
    """Orchestrates data collection from multiple sources"""
    
    def __init__(self):
        self.db = db_manager
        self.espn = espn_client
        self.nba = nba_client
    
    def collect_nba_teams(self):
        """Collect and store NBA teams"""
        logger.info("Collecting NBA teams...")
        try:
            teams = self.nba.get_all_teams()
            
            for team in teams:
                team_id = self.db.insert_team(
                    external_id=str(team['id']),
                    name=team['full_name'],
                    abbreviation=team['abbreviation'],
                    sport='NBA',
                    conference=None,  # Will be updated from ESPN if available
                    division=None
                )
                logger.debug(f"Inserted/updated NBA team: {team['full_name']} (ID: {team_id})")
            
            logger.info(f"✓ Collected {len(teams)} NBA teams")
            return True
        except Exception as e:
            logger.error(f"Error collecting NBA teams: {e}")
            return False
    
    def collect_nfl_teams(self):
        """Collect and store NFL teams"""
        logger.info("Collecting NFL teams...")
        try:
            data = self.espn.get_nfl_teams()
            if not data or 'sports' not in data:
                logger.warning("No NFL teams data received")
                return False
            
            teams = data['sports'][0].get('leagues', [{}])[0].get('teams', [])
            
            for team_data in teams:
                team = team_data.get('team', {})
                team_id = self.db.insert_team(
                    external_id=team.get('id'),
                    name=team.get('displayName'),
                    abbreviation=team.get('abbreviation'),
                    sport='NFL',
                    conference=team.get('groups', {}).get('parent', {}).get('name'),
                    division=team.get('groups', {}).get('name')
                )
                logger.debug(f"Inserted/updated NFL team: {team.get('displayName')} (ID: {team_id})")
            
            logger.info(f"✓ Collected {len(teams)} NFL teams")
            return True
        except Exception as e:
            logger.error(f"Error collecting NFL teams: {e}")
            return False
    
    def collect_nba_schedule(self, days_ahead: int = 7):
        """Collect NBA schedule for upcoming days"""
        logger.info(f"Collecting NBA schedule for next {days_ahead} days...")
        try:
            games_collected = 0
            
            for day_offset in range(days_ahead):
                date = datetime.now() + timedelta(days=day_offset)
                date_str = date.strftime('%Y-%m-%d')
                
                scoreboard_data = self.nba.get_scoreboard(date_str)
                if not scoreboard_data:
                    continue
                
                # Parse scoreboard data
                result_sets = scoreboard_data.get('resultSets', [])
                for result_set in result_sets:
                    if result_set.get('name') == 'GameHeader':
                        headers = result_set.get('headers', [])
                        games = result_set.get('rowSet', [])
                        
                        for game in games:
                            game_dict = dict(zip(headers, game))
                            
                            # Get team IDs
                            home_team = self.db.get_team_by_external_id(
                                str(game_dict.get('HOME_TEAM_ID')),
                                'NBA'
                            )
                            away_team = self.db.get_team_by_external_id(
                                str(game_dict.get('VISITOR_TEAM_ID')),
                                'NBA'
                            )
                            
                            if not home_team or not away_team:
                                logger.warning(f"Could not find teams for game {game_dict.get('GAME_ID')}")
                                continue
                            
                            # Insert game
                            game_id = self.db.insert_game(
                                external_id=game_dict.get('GAME_ID'),
                                date=date_str,
                                home_team_id=home_team['id'],
                                away_team_id=away_team['id'],
                                sport='NBA',
                                season=CURRENT_SEASON['nba'],
                                status=game_dict.get('GAME_STATUS_TEXT', 'scheduled').lower()
                            )
                            games_collected += 1
                            logger.debug(f"Inserted NBA game: {game_id}")
            
            logger.info(f"✓ Collected {games_collected} NBA games")
            return True
        except Exception as e:
            logger.error(f"Error collecting NBA schedule: {e}")
            return False
    
    def collect_nfl_schedule(self, weeks: int = 4):
        """Collect NFL schedule for upcoming weeks"""
        logger.info(f"Collecting NFL schedule for next {weeks} weeks...")
        try:
            games_collected = 0
            current_week = self._get_current_nfl_week()
            
            for week in range(current_week, min(current_week + weeks, 19)):
                scoreboard_data = self.espn.get_nfl_schedule(
                    season=int(CURRENT_SEASON['nfl']),
                    week=week
                )
                
                if not scoreboard_data or 'events' not in scoreboard_data:
                    continue
                
                for event in scoreboard_data['events']:
                    competition = event.get('competitions', [{}])[0]
                    competitors = competition.get('competitors', [])
                    
                    # Find home and away teams
                    home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                    away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                    
                    if not home_team or not away_team:
                        continue
                    
                    home_team_db = self.db.get_team_by_external_id(
                        home_team['team']['id'],
                        'NFL'
                    )
                    away_team_db = self.db.get_team_by_external_id(
                        away_team['team']['id'],
                        'NFL'
                    )
                    
                    if not home_team_db or not away_team_db:
                        continue
                    
                    # Parse date
                    game_date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                    
                    game_id = self.db.insert_game(
                        external_id=event['id'],
                        date=game_date.strftime('%Y-%m-%d'),
                        time=game_date.strftime('%H:%M:%S'),
                        home_team_id=home_team_db['id'],
                        away_team_id=away_team_db['id'],
                        sport='NFL',
                        season=CURRENT_SEASON['nfl'],
                        week=week,
                        status=competition.get('status', {}).get('type', {}).get('name', 'scheduled').lower(),
                        home_score=home_team.get('score'),
                        away_score=away_team.get('score')
                    )
                    games_collected += 1
                    logger.debug(f"Inserted NFL game: {game_id}")
            
            logger.info(f"✓ Collected {games_collected} NFL games")
            return True
        except Exception as e:
            logger.error(f"Error collecting NFL schedule: {e}")
            return False
    
    def collect_nba_player_stats(self, limit_players: int = None):
        """Collect NBA player game logs for the current season"""
        logger.info("Collecting NBA player statistics...")
        try:
            players = self.nba.get_all_players()
            stats_collected = 0
            
            # Limit to active players if needed
            if limit_players:
                players = players[:limit_players]
            
            for i, player in enumerate(players):
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{len(players)} players processed")
                
                player_id = str(player['id'])
                
                # Check if player exists in database
                player_db = self.db.get_player_by_external_id(player_id, 'NBA')
                if not player_db:
                    # Insert player (without team for now)
                    db_player_id = self.db.insert_player(
                        external_id=player_id,
                        name=player['full_name'],
                        sport='NBA',
                        is_active=player.get('is_active', True)
                    )
                else:
                    db_player_id = player_db['id']
                
                # Get game log
                game_log_data = self.nba.get_player_game_log(
                    player_id,
                    season=CURRENT_SEASON['nba']
                )
                
                if not game_log_data:
                    continue
                
                games = self.nba.parse_player_game_log(game_log_data)
                
                for game_stat in games:
                    # Find game in database
                    game_db = self.db.get_game_by_external_id(game_stat['game_id'])
                    if not game_db:
                        continue
                    
                    # Determine if home game
                    matchup = game_stat.get('matchup', '')
                    is_home = ' vs. ' in matchup
                    
                    # Insert stats
                    self.db.insert_player_game_stats(
                        player_id=db_player_id,
                        game_id=game_db['id'],
                        team_id=player_db['team_id'] if player_db else None,
                        is_home=is_home,
                        stats=game_stat['stats']
                    )
                    stats_collected += 1
            
            logger.info(f"✓ Collected {stats_collected} player game stats")
            return True
        except Exception as e:
            logger.error(f"Error collecting NBA player stats: {e}")
            return False
    
    def _get_current_nfl_week(self) -> int:
        """Estimate current NFL week based on date"""
        # NFL season typically starts first week of September
        now = datetime.now()
        season_start = datetime(int(CURRENT_SEASON['nfl']), 9, 1)
        
        if now < season_start:
            return 1
        
        weeks_passed = (now - season_start).days // 7
        return min(max(1, weeks_passed + 1), 18)
    
    def run_daily_collection(self, collect_stats: bool = False):
        """Run daily data collection routine"""
        logger.info("=" * 60)
        logger.info("Starting daily data collection")
        logger.info("=" * 60)
        
        results = {}
        
        # Collect teams (run once or periodically)
        results['nba_teams'] = self.collect_nba_teams()
        results['nfl_teams'] = self.collect_nfl_teams()
        
        # Collect schedules
        results['nba_schedule'] = self.collect_nba_schedule(days_ahead=7)
        results['nfl_schedule'] = self.collect_nfl_schedule(weeks=4)
        
        # Optionally collect player stats (can be time-consuming)
        if collect_stats:
            results['nba_stats'] = self.collect_nba_player_stats(limit_players=100)
        
        # Summary
        logger.info("=" * 60)
        logger.info("Data collection summary:")
        for task, success in results.items():
            status = "✓ Success" if success else "✗ Failed"
            logger.info(f"  {task}: {status}")
        logger.info("=" * 60)
        
        return all(results.values())


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Collect NFL and NBA betting data')
    parser.add_argument(
        '--with-stats',
        action='store_true',
        help='Also collect player statistics (time-consuming)'
    )
    parser.add_argument(
        '--teams-only',
        action='store_true',
        help='Only collect team data'
    )
    parser.add_argument(
        '--schedule-only',
        action='store_true',
        help='Only collect schedule data'
    )
    
    args = parser.parse_args()
    
    collector = DataCollector()
    
    try:
        if args.teams_only:
            logger.info("Running teams-only collection")
            collector.collect_nba_teams()
            collector.collect_nfl_teams()
        elif args.schedule_only:
            logger.info("Running schedule-only collection")
            collector.collect_nba_schedule()
            collector.collect_nfl_schedule()
        else:
            logger.info("Running full daily collection")
            collector.run_daily_collection(collect_stats=args.with_stats)
        
        logger.info("✓ Data collection completed successfully")
        return 0
    except KeyboardInterrupt:
        logger.warning("Data collection interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Data collection failed: {e}", exc_info=True)
        return 1
    finally:
        db_manager.close()


if __name__ == '__main__':
    sys.exit(main())
