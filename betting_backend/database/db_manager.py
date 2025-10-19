
"""
Database connection and management module
"""
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging
from typing import Optional, Dict, List, Any
from config import DB_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: Dict[str, str] = None):
        """Initialize database manager with connection pool"""
        self.config = config or DB_CONFIG
        self.pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **self.config
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict]]:
        """Execute a query and optionally fetch results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute a query multiple times with different parameters"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def insert_team(self, external_id: str, name: str, sport: str, 
                    abbreviation: str = None, conference: str = None, 
                    division: str = None) -> int:
        """Insert or update a team and return its ID"""
        query = """
            INSERT INTO teams (external_id, name, sport, abbreviation, conference, division)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (external_id, sport) 
            DO UPDATE SET 
                name = EXCLUDED.name,
                abbreviation = EXCLUDED.abbreviation,
                conference = EXCLUDED.conference,
                division = EXCLUDED.division,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        result = self.execute_query(query, (external_id, name, sport, abbreviation, conference, division))
        return result[0]['id']
    
    def insert_player(self, external_id: str, name: str, sport: str,
                     team_id: int = None, position: str = None, 
                     jersey_number: str = None, is_active: bool = True) -> int:
        """Insert or update a player and return its ID"""
        query = """
            INSERT INTO players (external_id, name, sport, team_id, position, jersey_number, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (external_id, sport)
            DO UPDATE SET 
                name = EXCLUDED.name,
                team_id = EXCLUDED.team_id,
                position = EXCLUDED.position,
                jersey_number = EXCLUDED.jersey_number,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        result = self.execute_query(query, (external_id, name, sport, team_id, position, jersey_number, is_active))
        return result[0]['id']
    
    def insert_game(self, external_id: str, date: str, home_team_id: int,
                   away_team_id: int, sport: str, season: str,
                   time: str = None, week: int = None, status: str = 'scheduled',
                   home_score: int = None, away_score: int = None) -> int:
        """Insert or update a game and return its ID"""
        query = """
            INSERT INTO games (external_id, date, time, home_team_id, away_team_id, 
                             sport, season, week, status, home_score, away_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (external_id)
            DO UPDATE SET 
                date = EXCLUDED.date,
                time = EXCLUDED.time,
                status = EXCLUDED.status,
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        result = self.execute_query(query, (external_id, date, time, home_team_id, 
                                           away_team_id, sport, season, week, 
                                           status, home_score, away_score))
        return result[0]['id']
    
    def insert_player_game_stats(self, player_id: int, game_id: int, 
                                team_id: int, is_home: bool, 
                                stats: Dict[str, Any]) -> int:
        """Insert or update player game stats and return its ID"""
        query = """
            INSERT INTO player_game_stats (player_id, game_id, team_id, is_home, stats)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (player_id, game_id)
            DO UPDATE SET 
                stats = EXCLUDED.stats,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        result = self.execute_query(query, (player_id, game_id, team_id, is_home, Json(stats)))
        return result[0]['id']
    
    def insert_projection(self, player_id: int, game_id: int, prop_type: str,
                         projected_value: float, confidence: float = None,
                         model_version: str = None, features: Dict = None) -> int:
        """Insert a projection"""
        query = """
            INSERT INTO projections (player_id, game_id, prop_type, projected_value, 
                                   confidence, model_version, features)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(query, (player_id, game_id, prop_type, 
                                           projected_value, confidence, 
                                           model_version, Json(features) if features else None))
        return result[0]['id']
    
    def insert_bet(self, date: str, entry_type: str, props: Dict, stake: float,
                  odds: float = None, outcome: str = 'pending', 
                  pnl: float = None, notes: str = None) -> int:
        """Insert a bet"""
        query = """
            INSERT INTO bets (date, entry_type, props, stake, odds, outcome, pnl, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(query, (date, entry_type, Json(props), 
                                           stake, odds, outcome, pnl, notes))
        return result[0]['id']
    
    def get_team_by_external_id(self, external_id: str, sport: str) -> Optional[Dict]:
        """Get team by external ID and sport"""
        query = "SELECT * FROM teams WHERE external_id = %s AND sport = %s"
        result = self.execute_query(query, (external_id, sport))
        return result[0] if result else None
    
    def get_player_by_external_id(self, external_id: str, sport: str) -> Optional[Dict]:
        """Get player by external ID and sport"""
        query = "SELECT * FROM players WHERE external_id = %s AND sport = %s"
        result = self.execute_query(query, (external_id, sport))
        return result[0] if result else None
    
    def get_game_by_external_id(self, external_id: str) -> Optional[Dict]:
        """Get game by external ID"""
        query = "SELECT * FROM games WHERE external_id = %s"
        result = self.execute_query(query, (external_id,))
        return result[0] if result else None
    
    def get_player_recent_stats(self, player_id: int, limit: int = 10) -> List[Dict]:
        """Get player's recent game stats"""
        query = """
            SELECT pgs.*, g.date, g.home_team_id, g.away_team_id
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.id
            WHERE pgs.player_id = %s AND g.status = 'completed'
            ORDER BY g.date DESC
            LIMIT %s
        """
        return self.execute_query(query, (player_id, limit))
    
    def get_upcoming_games(self, sport: str, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming games for a sport"""
        query = """
            SELECT * FROM upcoming_games_view
            WHERE sport = %s AND date <= CURRENT_DATE + INTERVAL '%s days'
            ORDER BY date, time
        """
        return self.execute_query(query, (sport, days_ahead))
    
    def close(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")


# Global database manager instance
db_manager = DatabaseManager()
