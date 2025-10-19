
-- NFL and NBA Betting Analysis Database Schema
-- Supports current season data with design for historical backfill

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS bets CASCADE;
DROP TABLE IF EXISTS projections CASCADE;
DROP TABLE IF EXISTS player_game_stats CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TYPE IF EXISTS sport_type CASCADE;
DROP TYPE IF EXISTS bet_outcome CASCADE;

-- Create custom types
CREATE TYPE sport_type AS ENUM ('NFL', 'NBA');
CREATE TYPE bet_outcome AS ENUM ('pending', 'win', 'loss', 'push', 'cancelled');

-- Teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE NOT NULL,  -- ESPN/NBA API team ID
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10),
    sport sport_type NOT NULL,
    conference VARCHAR(50),
    division VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_team_sport UNIQUE (external_id, sport)
);

-- Players table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE NOT NULL,  -- ESPN/NBA API player ID
    name VARCHAR(100) NOT NULL,
    team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    position VARCHAR(20),
    sport sport_type NOT NULL,
    jersey_number VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_player_sport UNIQUE (external_id, sport)
);

-- Games table
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE NOT NULL,  -- ESPN/NBA API game ID
    date DATE NOT NULL,
    time TIME,
    home_team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    sport sport_type NOT NULL,
    season VARCHAR(20) NOT NULL,  -- e.g., '2024-25' for NBA, '2024' for NFL
    week INTEGER,  -- For NFL only
    status VARCHAR(50) DEFAULT 'scheduled',  -- scheduled, in_progress, completed, postponed
    home_score INTEGER,
    away_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT different_teams CHECK (home_team_id != away_team_id)
);

-- Player game stats table (comprehensive stats in JSONB)
CREATE TABLE player_game_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    is_home BOOLEAN NOT NULL,
    stats JSONB NOT NULL,  -- Flexible storage for all stats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_player_game UNIQUE (player_id, game_id)
);

-- Projections table
CREATE TABLE projections (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    prop_type VARCHAR(50) NOT NULL,  -- e.g., 'points', 'rebounds', 'passing_yards'
    projected_value DECIMAL(10, 2) NOT NULL,
    confidence DECIMAL(5, 2),  -- Confidence score 0-100
    model_version VARCHAR(50),
    features JSONB,  -- Store features used for projection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_projection UNIQUE (player_id, game_id, prop_type, created_at)
);

-- Bets table
CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    entry_type VARCHAR(50) NOT NULL,  -- e.g., 'single', 'parlay', 'sgp'
    props JSONB NOT NULL,  -- Array of props with details
    stake DECIMAL(10, 2) NOT NULL,
    odds DECIMAL(10, 2),
    outcome bet_outcome DEFAULT 'pending',
    pnl DECIMAL(10, 2),  -- Profit and Loss
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization

-- Teams indexes
CREATE INDEX idx_teams_sport ON teams(sport);
CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_external_id ON teams(external_id);

-- Players indexes
CREATE INDEX idx_players_team_id ON players(team_id);
CREATE INDEX idx_players_sport ON players(sport);
CREATE INDEX idx_players_name ON players(name);
CREATE INDEX idx_players_external_id ON players(external_id);
CREATE INDEX idx_players_active ON players(is_active);

-- Games indexes
CREATE INDEX idx_games_date ON games(date);
CREATE INDEX idx_games_sport ON games(sport);
CREATE INDEX idx_games_season ON games(season);
CREATE INDEX idx_games_home_team ON games(home_team_id);
CREATE INDEX idx_games_away_team ON games(away_team_id);
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_games_external_id ON games(external_id);
CREATE INDEX idx_games_sport_season ON games(sport, season);
CREATE INDEX idx_games_date_sport ON games(date, sport);

-- Player game stats indexes
CREATE INDEX idx_pgs_player_id ON player_game_stats(player_id);
CREATE INDEX idx_pgs_game_id ON player_game_stats(game_id);
CREATE INDEX idx_pgs_team_id ON player_game_stats(team_id);
CREATE INDEX idx_pgs_player_game ON player_game_stats(player_id, game_id);
CREATE INDEX idx_pgs_stats ON player_game_stats USING GIN (stats);  -- GIN index for JSONB queries

-- Projections indexes
CREATE INDEX idx_projections_player_id ON projections(player_id);
CREATE INDEX idx_projections_game_id ON projections(game_id);
CREATE INDEX idx_projections_prop_type ON projections(prop_type);
CREATE INDEX idx_projections_created_at ON projections(created_at);
CREATE INDEX idx_projections_player_prop ON projections(player_id, prop_type);

-- Bets indexes
CREATE INDEX idx_bets_date ON bets(date);
CREATE INDEX idx_bets_outcome ON bets(outcome);
CREATE INDEX idx_bets_entry_type ON bets(entry_type);
CREATE INDEX idx_bets_props ON bets USING GIN (props);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_player_game_stats_updated_at BEFORE UPDATE ON player_game_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bets_updated_at BEFORE UPDATE ON bets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries

-- View for player stats with game and team info
CREATE OR REPLACE VIEW player_stats_view AS
SELECT 
    pgs.id,
    p.name as player_name,
    p.position,
    t.name as team_name,
    t.abbreviation as team_abbr,
    g.date as game_date,
    g.season,
    ht.name as home_team,
    at.name as away_team,
    pgs.is_home,
    g.status as game_status,
    pgs.stats,
    pgs.created_at
FROM player_game_stats pgs
JOIN players p ON pgs.player_id = p.id
JOIN teams t ON pgs.team_id = t.id
JOIN games g ON pgs.game_id = g.id
JOIN teams ht ON g.home_team_id = ht.id
JOIN teams at ON g.away_team_id = at.id;

-- View for upcoming games with team info
CREATE OR REPLACE VIEW upcoming_games_view AS
SELECT 
    g.id,
    g.external_id,
    g.date,
    g.time,
    g.sport,
    g.season,
    g.week,
    ht.name as home_team,
    ht.abbreviation as home_abbr,
    at.name as away_team,
    at.abbreviation as away_abbr,
    g.status
FROM games g
JOIN teams ht ON g.home_team_id = ht.id
JOIN teams at ON g.away_team_id = at.id
WHERE g.status = 'scheduled' AND g.date >= CURRENT_DATE
ORDER BY g.date, g.time;

-- View for projections with player and game info
CREATE OR REPLACE VIEW projections_view AS
SELECT 
    proj.id,
    p.name as player_name,
    p.position,
    t.name as team_name,
    g.date as game_date,
    ht.name as home_team,
    at.name as away_team,
    proj.prop_type,
    proj.projected_value,
    proj.confidence,
    proj.model_version,
    proj.created_at
FROM projections proj
JOIN players p ON proj.player_id = p.id
JOIN teams t ON p.team_id = t.id
JOIN games g ON proj.game_id = g.id
JOIN teams ht ON g.home_team_id = ht.id
JOIN teams at ON g.away_team_id = at.id;

COMMENT ON TABLE teams IS 'Teams for NFL and NBA';
COMMENT ON TABLE players IS 'Players with team associations';
COMMENT ON TABLE games IS 'Game schedule and results';
COMMENT ON TABLE player_game_stats IS 'Comprehensive player statistics per game stored in JSONB format';
COMMENT ON TABLE projections IS 'Model-generated projections for player props';
COMMENT ON TABLE bets IS 'Betting history and outcomes';

COMMENT ON COLUMN player_game_stats.stats IS 'JSONB field storing all stats: NBA (points, rebounds, assists, steals, blocks, turnovers, fg_made, fg_attempts, three_pt_made, three_pt_attempts, ft_made, ft_attempts, minutes), NFL (passing_yards, rushing_yards, receiving_yards, touchdowns, receptions, completions, attempts, interceptions)';
