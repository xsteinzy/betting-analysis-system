"""
NBA API integration using nba_api library with retry logic and caching
"""
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import wraps
import hashlib

from nba_api.stats.endpoints import (
    playergamelog,
    leaguegamefinder,
    teamgamelog,
    commonplayerinfo,
    commonteamroster,
    scoreboard,
    boxscoretraditionalv2,
    boxscoreadvancedv2
)
from nba_api.stats.static import teams, players

from config import NBA_API_CONFIG, CACHE_DIR, CACHE_EXPIRY

logger = logging.getLogger(__name__)


class NBAAPICacheManager:
    """Manages file-based caching for NBA API responses"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir) / 'nba_api'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key from endpoint and parameters"""
        cache_str = f"{endpoint}_{json.dumps(params, sort_keys=True) if params else ''}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, endpoint: str, params: Dict = None, expiry: int = 3600) -> Optional[Dict]:
        """Get cached data if not expired"""
        cache_key = self._get_cache_key(endpoint, params)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < timedelta(seconds=expiry):
                    logger.debug(f"Cache hit for {endpoint}")
                    return cached_data['data']
                else:
                    logger.debug(f"Cache expired for {endpoint}")
            except Exception as e:
                logger.warning(f"Error reading cache: {e}")
        
        return None
    
    def set(self, endpoint: str, data: Dict, params: Dict = None) -> None:
        """Cache data with timestamp"""
        cache_key = self._get_cache_key(endpoint, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
            logger.debug(f"Cached data for {endpoint}")
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")


def nba_retry_with_backoff(func):
    """Decorator for retry logic with exponential backoff for NBA API"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = NBA_API_CONFIG
        retry_attempts = config['retry_attempts']
        retry_delay = config['retry_delay']
        backoff_factor = config['backoff_factor']
        
        for attempt in range(retry_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == retry_attempts - 1:
                    logger.error(f"Max retries reached for {func.__name__}: {e}")
                    raise
                
                wait_time = retry_delay * (backoff_factor ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return None
    
    return wrapper


class NBAAPIClient:
    """Client for NBA API with caching and retry logic"""
    
    def __init__(self):
        self.cache = NBAAPICacheManager(CACHE_DIR)
        self.timeout = NBA_API_CONFIG['timeout']
    
    @nba_retry_with_backoff
    def _fetch_with_retry(self, endpoint_func, **kwargs):
        """Fetch data from NBA API endpoint with retry logic"""
        endpoint = endpoint_func(**kwargs)
        return endpoint.get_dict()
    
    def _get_with_cache(self, endpoint_name: str, endpoint_func, 
                       params: Dict, cache_expiry: int = None) -> Optional[Dict]:
        """Get data with caching"""
        expiry = cache_expiry or CACHE_EXPIRY['game_data']
        
        # Try cache first
        cached_data = self.cache.get(endpoint_name, params, expiry)
        if cached_data:
            return cached_data
        
        # Fetch from API
        try:
            data = self._fetch_with_retry(endpoint_func, **params)
            self.cache.set(endpoint_name, data, params)
            # NBA API rate limiting - be respectful
            time.sleep(0.6)  # Max ~100 requests per minute
            return data
        except Exception as e:
            logger.error(f"Error fetching from NBA API: {e}")
            return None
    
    def get_all_teams(self) -> List[Dict]:
        """Get all NBA teams (static data)"""
        logger.info("Fetching all NBA teams")
        return teams.get_teams()
    
    def get_all_players(self) -> List[Dict]:
        """Get all NBA players (static data)"""
        logger.info("Fetching all NBA players")
        return players.get_players()
    
    def get_player_info(self, player_id: str) -> Optional[Dict]:
        """Get detailed player information"""
        endpoint_name = f"commonplayerinfo_{player_id}"
        params = {'player_id': player_id}
        
        logger.info(f"Fetching player info for {player_id}")
        return self._get_with_cache(
            endpoint_name,
            commonplayerinfo.CommonPlayerInfo,
            params,
            CACHE_EXPIRY['player_data']
        )
    
    def get_player_game_log(self, player_id: str, season: str = '2024-25') -> Optional[Dict]:
        """
        Get player game log for a season
        
        Args:
            player_id: NBA player ID
            season: Season in format '2024-25'
        """
        endpoint_name = f"playergamelog_{player_id}_{season}"
        params = {
            'player_id': player_id,
            'season': season,
            'season_type_all_star': 'Regular Season'
        }
        
        logger.info(f"Fetching game log for player {player_id}, season {season}")
        return self._get_with_cache(
            endpoint_name,
            playergamelog.PlayerGameLog,
            params,
            CACHE_EXPIRY['player_data']
        )
    
    def get_team_roster(self, team_id: str, season: str = '2024-25') -> Optional[Dict]:
        """Get team roster"""
        endpoint_name = f"commonteamroster_{team_id}_{season}"
        params = {'team_id': team_id, 'season': season}
        
        logger.info(f"Fetching roster for team {team_id}, season {season}")
        return self._get_with_cache(
            endpoint_name,
            commonteamroster.CommonTeamRoster,
            params,
            CACHE_EXPIRY['team_data']
        )
    
    def get_team_game_log(self, team_id: str, season: str = '2024-25') -> Optional[Dict]:
        """Get team game log"""
        endpoint_name = f"teamgamelog_{team_id}_{season}"
        params = {
            'team_id': team_id,
            'season': season,
            'season_type_all_star': 'Regular Season'
        }
        
        logger.info(f"Fetching game log for team {team_id}, season {season}")
        return self._get_with_cache(
            endpoint_name,
            teamgamelog.TeamGameLog,
            params,
            CACHE_EXPIRY['game_data']
        )
    
    def get_scoreboard(self, game_date: str) -> Optional[Dict]:
        """
        Get scoreboard for a specific date
        
        Args:
            game_date: Date in format 'YYYY-MM-DD'
        """
        endpoint_name = f"scoreboard_{game_date}"
        # Convert date format for NBA API
        date_obj = datetime.strptime(game_date, '%Y-%m-%d')
        nba_date = date_obj.strftime('%m/%d/%Y')
        params = {'game_date': nba_date}
        
        logger.info(f"Fetching scoreboard for {game_date}")
        return self._get_with_cache(
            endpoint_name,
            scoreboard.Scoreboard,
            params,
            CACHE_EXPIRY['game_data']
        )
    
    def get_box_score_traditional(self, game_id: str) -> Optional[Dict]:
        """Get traditional box score for a game"""
        endpoint_name = f"boxscore_traditional_{game_id}"
        params = {'game_id': game_id}
        
        logger.info(f"Fetching traditional box score for game {game_id}")
        return self._get_with_cache(
            endpoint_name,
            boxscoretraditionalv2.BoxScoreTraditionalV2,
            params,
            CACHE_EXPIRY['game_data']
        )
    
    def get_box_score_advanced(self, game_id: str) -> Optional[Dict]:
        """Get advanced box score for a game"""
        endpoint_name = f"boxscore_advanced_{game_id}"
        params = {'game_id': game_id}
        
        logger.info(f"Fetching advanced box score for game {game_id}")
        return self._get_with_cache(
            endpoint_name,
            boxscoreadvancedv2.BoxScoreAdvancedV2,
            params,
            CACHE_EXPIRY['game_data']
        )
    
    def parse_player_game_log(self, game_log_data: Dict) -> List[Dict[str, Any]]:
        """Parse player game log data to extract statistics"""
        player_stats = []
        
        try:
            if 'resultSets' in game_log_data and len(game_log_data['resultSets']) > 0:
                result_set = game_log_data['resultSets'][0]
                headers = result_set.get('headers', [])
                rows = result_set.get('rowSet', [])
                
                for row in rows:
                    stats = dict(zip(headers, row))
                    # Convert to our standard format
                    player_stats.append({
                        'game_id': stats.get('Game_ID'),
                        'game_date': stats.get('GAME_DATE'),
                        'matchup': stats.get('MATCHUP'),
                        'stats': {
                            'minutes': stats.get('MIN'),
                            'points': stats.get('PTS'),
                            'rebounds': stats.get('REB'),
                            'assists': stats.get('AST'),
                            'steals': stats.get('STL'),
                            'blocks': stats.get('BLK'),
                            'turnovers': stats.get('TOV'),
                            'fg_made': stats.get('FGM'),
                            'fg_attempts': stats.get('FGA'),
                            'fg_percentage': stats.get('FG_PCT'),
                            'three_pt_made': stats.get('FG3M'),
                            'three_pt_attempts': stats.get('FG3A'),
                            'three_pt_percentage': stats.get('FG3_PCT'),
                            'ft_made': stats.get('FTM'),
                            'ft_attempts': stats.get('FTA'),
                            'ft_percentage': stats.get('FT_PCT'),
                            'offensive_rebounds': stats.get('OREB'),
                            'defensive_rebounds': stats.get('DREB'),
                            'personal_fouls': stats.get('PF'),
                            'plus_minus': stats.get('PLUS_MINUS')
                        }
                    })
        except Exception as e:
            logger.error(f"Error parsing player game log: {e}")
        
        return player_stats
    
    def parse_box_score(self, box_score_data: Dict) -> Dict[str, List[Dict[str, Any]]]:
        """Parse box score data to extract player statistics"""
        team_stats = {'home': [], 'away': []}
        
        try:
            if 'resultSets' in box_score_data:
                for result_set in box_score_data['resultSets']:
                    if result_set.get('name') == 'PlayerStats':
                        headers = result_set.get('headers', [])
                        rows = result_set.get('rowSet', [])
                        
                        for row in rows:
                            stats = dict(zip(headers, row))
                            player_stat = {
                                'player_id': stats.get('PLAYER_ID'),
                                'player_name': stats.get('PLAYER_NAME'),
                                'team_id': stats.get('TEAM_ID'),
                                'stats': {
                                    'minutes': stats.get('MIN'),
                                    'points': stats.get('PTS'),
                                    'rebounds': stats.get('REB'),
                                    'assists': stats.get('AST'),
                                    'steals': stats.get('STL'),
                                    'blocks': stats.get('BLK'),
                                    'turnovers': stats.get('TOV'),
                                    'fg_made': stats.get('FGM'),
                                    'fg_attempts': stats.get('FGA'),
                                    'fg_percentage': stats.get('FG_PCT'),
                                    'three_pt_made': stats.get('FG3M'),
                                    'three_pt_attempts': stats.get('FG3A'),
                                    'three_pt_percentage': stats.get('FG3_PCT'),
                                    'ft_made': stats.get('FTM'),
                                    'ft_attempts': stats.get('FTA'),
                                    'ft_percentage': stats.get('FT_PCT')
                                }
                            }
                            
                            # Determine home/away (would need game context)
                            team_stats['home'].append(player_stat)
        except Exception as e:
            logger.error(f"Error parsing box score: {e}")
        
        return team_stats


# Global NBA API client instance
nba_client = NBAAPIClient()
