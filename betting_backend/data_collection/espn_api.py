
"""
ESPN Hidden API integration with retry logic, exponential backoff, and caching
"""
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import wraps
import hashlib

from config import ESPN_API_CONFIG, CACHE_DIR, CACHE_EXPIRY

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages file-based caching for API responses"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key from URL and parameters"""
        cache_str = f"{url}_{json.dumps(params, sort_keys=True) if params else ''}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, url: str, params: Dict = None, expiry: int = 3600) -> Optional[Dict]:
        """Get cached data if not expired"""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < timedelta(seconds=expiry):
                    logger.debug(f"Cache hit for {url}")
                    return cached_data['data']
                else:
                    logger.debug(f"Cache expired for {url}")
            except Exception as e:
                logger.warning(f"Error reading cache: {e}")
        
        return None
    
    def set(self, url: str, data: Dict, params: Dict = None) -> None:
        """Cache data with timestamp"""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
            logger.debug(f"Cached data for {url}")
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")


def retry_with_backoff(func):
    """Decorator for retry logic with exponential backoff"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = ESPN_API_CONFIG
        retry_attempts = config['retry_attempts']
        retry_delay = config['retry_delay']
        backoff_factor = config['backoff_factor']
        
        for attempt in range(retry_attempts):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == retry_attempts - 1:
                    logger.error(f"Max retries reached for {func.__name__}: {e}")
                    raise
                
                wait_time = retry_delay * (backoff_factor ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return None
    
    return wrapper


class ESPNAPIClient:
    """Client for ESPN Hidden API with caching and retry logic"""
    
    def __init__(self):
        self.base_url = ESPN_API_CONFIG['base_url']
        self.timeout = ESPN_API_CONFIG['timeout']
        self.cache = CacheManager(CACHE_DIR / 'espn')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @retry_with_backoff
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make HTTP request with retry logic"""
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def _get_with_cache(self, url: str, params: Dict = None, 
                       cache_expiry: int = None) -> Optional[Dict]:
        """Get data with caching"""
        expiry = cache_expiry or CACHE_EXPIRY['game_data']
        
        # Try cache first
        cached_data = self.cache.get(url, params, expiry)
        if cached_data:
            return cached_data
        
        # Fetch from API
        try:
            data = self._make_request(url, params)
            self.cache.set(url, data, params)
            return data
        except Exception as e:
            logger.error(f"Error fetching from ESPN API: {e}")
            return None
    
    def get_nfl_scoreboard(self, date: str = None) -> Optional[Dict]:
        """
        Get NFL scoreboard for a specific date
        
        Args:
            date: Date in YYYYMMDD format (default: today)
        """
        url = f"{self.base_url}/football/nfl/scoreboard"
        params = {}
        if date:
            params['dates'] = date
        
        logger.info(f"Fetching NFL scoreboard for date: {date or 'today'}")
        return self._get_with_cache(url, params, CACHE_EXPIRY['game_data'])
    
    def get_nba_scoreboard(self, date: str = None) -> Optional[Dict]:
        """
        Get NBA scoreboard for a specific date
        
        Args:
            date: Date in YYYYMMDD format (default: today)
        """
        url = f"{self.base_url}/basketball/nba/scoreboard"
        params = {}
        if date:
            params['dates'] = date
        
        logger.info(f"Fetching NBA scoreboard for date: {date or 'today'}")
        return self._get_with_cache(url, params, CACHE_EXPIRY['game_data'])
    
    def get_nfl_teams(self) -> Optional[Dict]:
        """Get all NFL teams"""
        url = f"{self.base_url}/football/nfl/teams"
        logger.info("Fetching NFL teams")
        return self._get_with_cache(url, cache_expiry=CACHE_EXPIRY['team_data'])
    
    def get_nba_teams(self) -> Optional[Dict]:
        """Get all NBA teams"""
        url = f"{self.base_url}/basketball/nba/teams"
        logger.info("Fetching NBA teams")
        return self._get_with_cache(url, cache_expiry=CACHE_EXPIRY['team_data'])
    
    def get_nfl_team_roster(self, team_id: str) -> Optional[Dict]:
        """Get NFL team roster"""
        url = f"{self.base_url}/football/nfl/teams/{team_id}/roster"
        logger.info(f"Fetching NFL roster for team {team_id}")
        return self._get_with_cache(url, cache_expiry=CACHE_EXPIRY['player_data'])
    
    def get_nba_team_roster(self, team_id: str) -> Optional[Dict]:
        """Get NBA team roster"""
        url = f"{self.base_url}/basketball/nba/teams/{team_id}/roster"
        logger.info(f"Fetching NBA roster for team {team_id}")
        return self._get_with_cache(url, cache_expiry=CACHE_EXPIRY['player_data'])
    
    def get_nfl_player_stats(self, player_id: str) -> Optional[Dict]:
        """Get NFL player statistics"""
        url = f"{self.base_url}/football/nfl/athletes/{player_id}/statistics"
        logger.info(f"Fetching NFL stats for player {player_id}")
        return self._get_with_cache(url, cache_expiry=CACHE_EXPIRY['player_data'])
    
    def get_nba_player_stats(self, player_id: str) -> Optional[Dict]:
        """Get NBA player statistics"""
        url = f"{self.base_url}/basketball/nba/athletes/{player_id}/statistics"
        logger.info(f"Fetching NBA stats for player {player_id}")
        return self._get_with_cache(url, cache_expiry=CACHE_EXPIRY['player_data'])
    
    def get_nfl_schedule(self, season: int, week: int = None) -> Optional[Dict]:
        """Get NFL schedule for a season/week"""
        url = f"{self.base_url}/football/nfl/scoreboard"
        params = {'seasontype': 2, 'week': week} if week else {'seasontype': 2}
        
        logger.info(f"Fetching NFL schedule for season {season}, week {week or 'all'}")
        return self._get_with_cache(url, params, CACHE_EXPIRY['schedule_data'])
    
    def get_nba_schedule(self, date: str = None) -> Optional[Dict]:
        """Get NBA schedule"""
        url = f"{self.base_url}/basketball/nba/scoreboard"
        params = {'dates': date} if date else {}
        
        logger.info(f"Fetching NBA schedule for date {date or 'today'}")
        return self._get_with_cache(url, params, CACHE_EXPIRY['schedule_data'])
    
    def get_game_details(self, sport: str, game_id: str) -> Optional[Dict]:
        """Get detailed game information"""
        sport_path = 'football/nfl' if sport == 'NFL' else 'basketball/nba'
        url = f"{self.base_url}/{sport_path}/summary"
        params = {'event': game_id}
        
        logger.info(f"Fetching game details for {sport} game {game_id}")
        return self._get_with_cache(url, params, CACHE_EXPIRY['game_data'])
    
    def parse_nfl_game_stats(self, game_data: Dict) -> List[Dict[str, Any]]:
        """Parse NFL game data to extract player statistics"""
        player_stats = []
        
        try:
            if 'boxscore' in game_data and 'players' in game_data['boxscore']:
                for team in game_data['boxscore']['players']:
                    team_id = team.get('team', {}).get('id')
                    
                    for stat_group in team.get('statistics', []):
                        for athlete in stat_group.get('athletes', []):
                            player_id = athlete.get('athlete', {}).get('id')
                            player_name = athlete.get('athlete', {}).get('displayName')
                            
                            stats = {}
                            for stat in athlete.get('stats', []):
                                stat_name = stat.lower().replace(' ', '_')
                                stats[stat_name] = stat
                            
                            player_stats.append({
                                'player_id': player_id,
                                'player_name': player_name,
                                'team_id': team_id,
                                'stats': stats
                            })
        except Exception as e:
            logger.error(f"Error parsing NFL game stats: {e}")
        
        return player_stats
    
    def parse_nba_game_stats(self, game_data: Dict) -> List[Dict[str, Any]]:
        """Parse NBA game data to extract player statistics"""
        player_stats = []
        
        try:
            if 'boxscore' in game_data and 'players' in game_data['boxscore']:
                for team in game_data['boxscore']['players']:
                    team_id = team.get('team', {}).get('id')
                    
                    for stat_group in team.get('statistics', []):
                        for athlete in stat_group.get('athletes', []):
                            player_id = athlete.get('athlete', {}).get('id')
                            player_name = athlete.get('athlete', {}).get('displayName')
                            
                            stats = {}
                            for stat in athlete.get('stats', []):
                                stat_name = stat.lower().replace(' ', '_')
                                stats[stat_name] = stat
                            
                            player_stats.append({
                                'player_id': player_id,
                                'player_name': player_name,
                                'team_id': team_id,
                                'stats': stats
                            })
        except Exception as e:
            logger.error(f"Error parsing NBA game stats: {e}")
        
        return player_stats


# Global ESPN API client instance
espn_client = ESPNAPIClient()
