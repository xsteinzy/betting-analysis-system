
-- Migration: Add backtest_results table for storing backtesting results
-- Created: 2025-10-19

-- Create backtest_results table
CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    sport VARCHAR(10),
    entry_size INTEGER,
    confidence_threshold INTEGER,
    ev_threshold DECIMAL(5,2),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Bet counts
    total_bets INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    
    -- Performance metrics
    win_rate DECIMAL(5,2),
    total_profit DECIMAL(10,2),
    total_staked DECIMAL(10,2),
    roi DECIMAL(5,2),
    max_drawdown DECIMAL(10,2),
    sharpe_ratio DECIMAL(5,2),
    profit_factor DECIMAL(5,2),
    
    -- Streak metrics
    longest_win_streak INTEGER DEFAULT 0,
    longest_loss_streak INTEGER DEFAULT 0,
    
    -- Bankroll management
    starting_bankroll DECIMAL(10,2),
    ending_bankroll DECIMAL(10,2),
    bankroll_strategy VARCHAR(50),
    avg_bet_size DECIMAL(10,2),
    
    -- Detailed results
    best_props JSONB,
    prop_performance JSONB,
    daily_results JSONB,
    insights JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_win_rate CHECK (win_rate >= 0 AND win_rate <= 100),
    CONSTRAINT valid_entry_size CHECK (entry_size >= 2 AND entry_size <= 5),
    CONSTRAINT valid_dates CHECK (end_date >= start_date)
);

-- Create indexes for faster queries
CREATE INDEX idx_backtest_strategy ON backtest_results(strategy_name);
CREATE INDEX idx_backtest_sport ON backtest_results(sport);
CREATE INDEX idx_backtest_dates ON backtest_results(start_date, end_date);
CREATE INDEX idx_backtest_entry_size ON backtest_results(entry_size);
CREATE INDEX idx_backtest_created ON backtest_results(created_at DESC);
CREATE INDEX idx_backtest_roi ON backtest_results(roi DESC);
CREATE INDEX idx_backtest_win_rate ON backtest_results(win_rate DESC);

-- Create GIN indexes for JSONB columns for faster queries
CREATE INDEX idx_backtest_best_props ON backtest_results USING GIN (best_props);
CREATE INDEX idx_backtest_insights ON backtest_results USING GIN (insights);

-- Create trigger for updated_at
CREATE TRIGGER update_backtest_results_updated_at 
    BEFORE UPDATE ON backtest_results
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for quick summary statistics
CREATE OR REPLACE VIEW backtest_summary_view AS
SELECT 
    strategy_name,
    sport,
    entry_size,
    COUNT(*) as num_backtests,
    AVG(win_rate) as avg_win_rate,
    AVG(roi) as avg_roi,
    AVG(total_profit) as avg_profit,
    MAX(roi) as max_roi,
    MIN(roi) as min_roi,
    MAX(created_at) as last_run
FROM backtest_results
GROUP BY strategy_name, sport, entry_size
ORDER BY avg_roi DESC;

COMMENT ON TABLE backtest_results IS 'Stores results from backtesting betting strategies on historical data';
COMMENT ON COLUMN backtest_results.strategy_name IS 'Name of the betting strategy tested';
COMMENT ON COLUMN backtest_results.best_props IS 'JSONB array of best performing prop types with their metrics';
COMMENT ON COLUMN backtest_results.prop_performance IS 'JSONB object with detailed performance by prop type';
COMMENT ON COLUMN backtest_results.daily_results IS 'JSONB array of daily performance metrics for charting';
COMMENT ON COLUMN backtest_results.insights IS 'JSONB array of actionable insights generated from backtest';

