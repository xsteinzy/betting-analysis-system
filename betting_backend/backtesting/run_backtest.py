#!/usr/bin/env python3
"""
Main Backtesting Runner
Command-line tool to run backtests on historical prediction data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from database.db_manager import DatabaseManager
from backtesting.strategy_simulator import StrategySimulator, BettingResult
from backtesting.performance_analyzer import PerformanceAnalyzer
from backtesting.insights_generator import InsightsGenerator
from backtesting.config import (
    DEFAULT_BACKTEST_PARAMS,
    BETTING_STRATEGIES,
    CONFIDENCE_THRESHOLDS,
    EV_THRESHOLDS,
    PROP_TYPES
)
from psycopg2.extras import Json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BacktestRunner:
    """
    Main backtesting orchestrator
    Fetches data, runs simulations, analyzes results, generates insights
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def fetch_historical_predictions(
        self,
        start_date: str,
        end_date: str,
        sport: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch historical predictions from database
        """
        self.logger.info(f"Fetching predictions from {start_date} to {end_date}")
        
        query = """
            SELECT 
                p.id,
                p.player_id,
                p.game_id,
                p.prop_type,
                p.projected_value,
                p.confidence,
                p.model_version,
                pl.name as player_name,
                g.date as game_date,
                g.sport,
                t.name as team_name
            FROM projections p
            JOIN players pl ON p.player_id = pl.id
            JOIN games g ON p.game_id = g.id
            JOIN teams t ON pl.team_id = t.id
            WHERE g.date BETWEEN %s AND %s
            AND g.status = 'completed'
        """
        
        params = [start_date, end_date]
        
        if sport:
            query += " AND g.sport = %s"
            params.append(sport)
        
        query += " ORDER BY g.date, p.player_id"
        
        predictions = self.db.execute_query(query, tuple(params))
        
        # Calculate expected value (simplified - assumes fair odds)
        for pred in predictions:
            confidence = pred.get('confidence', 0)
            if confidence > 50:
                pred['expected_value'] = (confidence - 50) * 0.5  # Simplified EV calculation
            else:
                pred['expected_value'] = 0
        
        self.logger.info(f"Fetched {len(predictions)} predictions")
        return predictions
    
    def fetch_actual_outcomes(
        self,
        start_date: str,
        end_date: str,
        sport: Optional[str] = None
    ) -> Dict:
        """
        Fetch actual game outcomes from database
        Returns dict mapping (player_id, game_id, prop_type) to actual value
        """
        self.logger.info(f"Fetching actual outcomes from {start_date} to {end_date}")
        
        query = """
            SELECT 
                pgs.player_id,
                pgs.game_id,
                pgs.stats,
                g.sport
            FROM player_game_stats pgs
            JOIN games g ON pgs.game_id = g.id
            WHERE g.date BETWEEN %s AND %s
            AND g.status = 'completed'
        """
        
        params = [start_date, end_date]
        
        if sport:
            query += " AND g.sport = %s"
            params.append(sport)
        
        results = self.db.execute_query(query, tuple(params))
        
        # Build lookup dictionary
        outcomes = {}
        
        for row in results:
            player_id = row['player_id']
            game_id = row['game_id']
            stats = row['stats']
            
            # Map each stat to a prop type
            stat_mapping = {
                # NBA stats
                'points': 'points',
                'rebounds': 'rebounds',
                'assists': 'assists',
                'steals': 'steals',
                'blocks': 'blocks',
                'three_pt_made': 'three_pointers_made',
                # NFL stats
                'passing_yards': 'passing_yards',
                'rushing_yards': 'rushing_yards',
                'receiving_yards': 'receiving_yards',
                'receptions': 'receptions',
                'passing_touchdowns': 'passing_touchdowns',
                'rushing_touchdowns': 'rushing_touchdowns',
                'receiving_touchdowns': 'receiving_touchdowns',
                'completions': 'completions',
                'attempts': 'pass_attempts',
                'interceptions': 'interceptions'
            }
            
            for stat_key, prop_type in stat_mapping.items():
                if stat_key in stats:
                    key = (player_id, game_id, prop_type)
                    outcomes[key] = {'value': stats[stat_key]}
            
            # Combo props (NBA)
            if 'points' in stats and 'rebounds' in stats and 'assists' in stats:
                key = (player_id, game_id, 'points_rebounds_assists')
                outcomes[key] = {'value': stats['points'] + stats['rebounds'] + stats['assists']}
            
            if 'points' in stats and 'rebounds' in stats:
                key = (player_id, game_id, 'points_rebounds')
                outcomes[key] = {'value': stats['points'] + stats['rebounds']}
            
            if 'points' in stats and 'assists' in stats:
                key = (player_id, game_id, 'points_assists')
                outcomes[key] = {'value': stats['points'] + stats['assists']}
            
            if 'rebounds' in stats and 'assists' in stats:
                key = (player_id, game_id, 'rebounds_assists')
                outcomes[key] = {'value': stats['rebounds'] + stats['assists']}
        
        self.logger.info(f"Fetched {len(outcomes)} actual outcomes")
        return outcomes
    
    def run_backtest(
        self,
        strategy_name: str,
        start_date: str,
        end_date: str,
        sport: Optional[str] = None,
        confidence_threshold: float = 70,
        ev_threshold: float = 5,
        prop_types: Optional[List[str]] = None,
        entry_sizes: List[int] = [2, 3, 4, 5],
        starting_bankroll: float = 1000,
        bet_size: float = 50,
        bankroll_strategy: str = 'flat'
    ) -> Dict:
        """
        Run a complete backtest with specified parameters
        """
        self.logger.info(f"Running {strategy_name} backtest")
        
        # Fetch data
        predictions = self.fetch_historical_predictions(start_date, end_date, sport)
        outcomes = self.fetch_actual_outcomes(start_date, end_date, sport)
        
        if not predictions:
            self.logger.warning("No predictions found for specified date range")
            return None
        
        # Initialize simulator
        simulator = StrategySimulator(predictions, outcomes)
        
        # Run appropriate strategy
        if strategy_name == 'confidence_based':
            result = simulator.simulate_confidence_based(
                confidence_threshold,
                entry_sizes,
                starting_bankroll,
                bet_size,
                bankroll_strategy,
                sport
            )
        
        elif strategy_name == 'value_based':
            result = simulator.simulate_value_based(
                ev_threshold,
                entry_sizes,
                starting_bankroll,
                bet_size,
                bankroll_strategy,
                sport
            )
        
        elif strategy_name == 'prop_specific':
            result = simulator.simulate_prop_specific(
                prop_types or [],
                entry_sizes,
                starting_bankroll,
                bet_size,
                confidence_threshold,
                bankroll_strategy,
                sport
            )
        
        elif strategy_name == 'composite':
            result = simulator.simulate_composite(
                confidence_threshold,
                ev_threshold,
                prop_types,
                entry_sizes,
                starting_bankroll,
                bet_size,
                bankroll_strategy,
                sport
            )
        
        else:
            self.logger.error(f"Unknown strategy: {strategy_name}")
            return None
        
        # Analyze results
        analyzer = PerformanceAnalyzer(result)
        analysis = analyzer.generate_summary_report()
        
        # Generate insights
        insights_gen = InsightsGenerator(analyzer)
        insights = insights_gen.generate_all_insights()
        
        # Prepare result package
        backtest_result = {
            'strategy_name': strategy_name,
            'parameters': {
                'start_date': start_date,
                'end_date': end_date,
                'sport': sport,
                'confidence_threshold': confidence_threshold,
                'ev_threshold': ev_threshold,
                'prop_types': prop_types,
                'entry_sizes': entry_sizes,
                'starting_bankroll': starting_bankroll,
                'bet_size': bet_size,
                'bankroll_strategy': bankroll_strategy
            },
            'performance': {
                'total_bets': result.total_bets,
                'wins': result.wins,
                'losses': result.losses,
                'win_rate': result.win_rate,
                'total_profit': result.total_profit,
                'total_staked': result.total_staked,
                'roi': result.roi,
                'max_drawdown': result.max_drawdown,
                'sharpe_ratio': result.sharpe_ratio,
                'profit_factor': result.profit_factor,
                'longest_win_streak': result.longest_win_streak,
                'longest_loss_streak': result.longest_loss_streak,
                'starting_bankroll': result.starting_bankroll,
                'ending_bankroll': result.ending_bankroll,
                'avg_bet_size': result.avg_bet_size
            },
            'analysis': analysis,
            'insights': insights
        }
        
        return backtest_result
    
    def save_backtest_results(self, backtest_result: Dict) -> int:
        """
        Save backtest results to database
        """
        self.logger.info("Saving backtest results to database")
        
        params = backtest_result['parameters']
        perf = backtest_result['performance']
        analysis = backtest_result['analysis']
        
        # Extract best props from analysis
        best_props = []
        if 'by_prop_type' in analysis:
            sorted_props = sorted(
                analysis['by_prop_type'].items(),
                key=lambda x: x[1]['win_rate'],
                reverse=True
            )
            best_props = [
                {
                    'prop_type': prop,
                    'win_rate': data['win_rate'],
                    'appearances': data['appearances']
                }
                for prop, data in sorted_props[:5]
            ]
        
        query = """
            INSERT INTO backtest_results (
                strategy_name, sport, entry_size, confidence_threshold, ev_threshold,
                start_date, end_date, total_bets, wins, losses, win_rate,
                total_profit, total_staked, roi, max_drawdown, sharpe_ratio,
                profit_factor, longest_win_streak, longest_loss_streak,
                starting_bankroll, ending_bankroll, bankroll_strategy, avg_bet_size,
                best_props, prop_performance, daily_results, insights
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        # For entry_size, use NULL if testing multiple sizes
        entry_size = None
        if len(params['entry_sizes']) == 1:
            entry_size = params['entry_sizes'][0]
        
        result = self.db.execute_query(query, (
            backtest_result['strategy_name'],
            params['sport'],
            entry_size,
            params['confidence_threshold'],
            params['ev_threshold'],
            params['start_date'],
            params['end_date'],
            perf['total_bets'],
            perf['wins'],
            perf['losses'],
            perf['win_rate'],
            perf['total_profit'],
            perf['total_staked'],
            perf['roi'],
            perf['max_drawdown'],
            perf['sharpe_ratio'],
            perf['profit_factor'],
            perf['longest_win_streak'],
            perf['longest_loss_streak'],
            perf['starting_bankroll'],
            perf['ending_bankroll'],
            params['bankroll_strategy'],
            perf['avg_bet_size'],
            Json(best_props),
            Json(analysis.get('by_prop_type', {})),
            Json(analysis.get('daily_results', [])),
            Json(backtest_result['insights'])
        ))
        
        backtest_id = result[0]['id']
        self.logger.info(f"Saved backtest results with ID: {backtest_id}")
        return backtest_id


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Run backtests on historical betting predictions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Confidence-based strategy for last 30 days
  python run_backtest.py --start-date 2024-09-19 --end-date 2024-10-19 \\
    --strategy confidence_based --confidence-threshold 75
  
  # NBA-only value-based strategy
  python run_backtest.py --start-date 2024-09-01 --end-date 2024-10-19 \\
    --strategy value_based --sport NBA --ev-threshold 10
  
  # Prop-specific strategy for points and assists
  python run_backtest.py --start-date 2024-09-01 --end-date 2024-10-19 \\
    --strategy prop_specific --props points assists --sport NBA
  
  # Composite strategy with multiple filters
  python run_backtest.py --start-date 2024-09-01 --end-date 2024-10-19 \\
    --strategy composite --confidence-threshold 75 --ev-threshold 5 \\
    --entry-sizes 2 3 --bankroll 2000 --bet-size 100
        """
    )
    
    # Date parameters
    parser.add_argument('--start-date', type=str, required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True,
                        help='End date (YYYY-MM-DD)')
    
    # Strategy parameters
    parser.add_argument('--strategy', type=str, required=True,
                        choices=['confidence_based', 'value_based', 'prop_specific', 'composite'],
                        help='Betting strategy to test')
    parser.add_argument('--sport', type=str, choices=['NBA', 'NFL'],
                        help='Filter by sport (default: both)')
    parser.add_argument('--confidence-threshold', type=float, default=70,
                        help='Minimum confidence threshold (default: 70)')
    parser.add_argument('--ev-threshold', type=float, default=5,
                        help='Minimum expected value threshold (default: 5)')
    parser.add_argument('--props', nargs='+',
                        help='Specific prop types to focus on')
    parser.add_argument('--entry-sizes', nargs='+', type=int, default=[2, 3, 4, 5],
                        help='Entry sizes to test (default: 2 3 4 5)')
    
    # Bankroll parameters
    parser.add_argument('--bankroll', type=float, default=1000,
                        help='Starting bankroll (default: 1000)')
    parser.add_argument('--bet-size', type=float, default=50,
                        help='Bet size or percentage (default: 50)')
    parser.add_argument('--bankroll-strategy', type=str,
                        choices=['flat', 'percentage', 'kelly'], default='flat',
                        help='Bankroll management strategy (default: flat)')
    
    # Output parameters
    parser.add_argument('--save', action='store_true',
                        help='Save results to database')
    parser.add_argument('--output', type=str,
                        help='Save results to JSON file')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Initialize runner
    runner = BacktestRunner(db)
    
    # Run backtest
    logger.info(f"Starting backtest: {args.strategy}")
    logger.info(f"Date range: {args.start_date} to {args.end_date}")
    
    try:
        result = runner.run_backtest(
            strategy_name=args.strategy,
            start_date=args.start_date,
            end_date=args.end_date,
            sport=args.sport,
            confidence_threshold=args.confidence_threshold,
            ev_threshold=args.ev_threshold,
            prop_types=args.props,
            entry_sizes=args.entry_sizes,
            starting_bankroll=args.bankroll,
            bet_size=args.bet_size,
            bankroll_strategy=args.bankroll_strategy
        )
        
        if result is None:
            logger.error("Backtest failed")
            return 1
        
        # Display results
        print("\n" + "="*80)
        print(f"BACKTEST RESULTS: {args.strategy.upper()}")
        print("="*80)
        
        perf = result['performance']
        print(f"\n📊 Performance Summary:")
        print(f"  Total Bets: {perf['total_bets']}")
        print(f"  Wins: {perf['wins']} | Losses: {perf['losses']}")
        print(f"  Win Rate: {perf['win_rate']}%")
        print(f"  Total Profit: ${perf['total_profit']:.2f}")
        print(f"  ROI: {perf['roi']:.2f}%")
        print(f"  Max Drawdown: {perf['max_drawdown']:.2f}%")
        print(f"  Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
        print(f"  Bankroll: ${perf['starting_bankroll']:.2f} → ${perf['ending_bankroll']:.2f}")
        
        print(f"\n💡 Key Insights:")
        for i, insight in enumerate(result['insights'][:5], 1):
            icon = "✅" if insight['type'] == 'success' else "⚠️" if insight['type'] == 'warning' else "ℹ️"
            print(f"  {i}. {icon} {insight['title']}")
            print(f"     {insight['message']}")
        
        # Save to database
        if args.save:
            backtest_id = runner.save_backtest_results(result)
            print(f"\n💾 Results saved to database (ID: {backtest_id})")
        
        # Save to file
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📁 Results saved to {args.output}")
        
        print("\n" + "="*80)
        
        return 0
    
    except Exception as e:
        logger.error(f"Error running backtest: {e}", exc_info=True)
        return 1
    
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
