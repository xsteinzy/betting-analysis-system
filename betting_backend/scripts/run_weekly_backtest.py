
#!/usr/bin/env python3
"""
Weekly Backtesting Automation Script
Runs backtests on recent data and updates database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from backtesting.run_backtest import BacktestRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weekly_backtest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeeklyBacktester:
    """
    Automated backtesting for weekly updates
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.runner = BacktestRunner(self.db)
        self.logger = logging.getLogger(__name__)
    
    def run_weekly_backtests(self):
        """
        Run multiple backtests with different strategies
        """
        self.logger.info("Starting weekly backtesting automation")
        
        # Calculate date range (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        self.logger.info(f"Testing date range: {start_str} to {end_str}")
        
        # Define strategies to test
        strategies = [
            {
                'name': 'confidence_based',
                'params': {
                    'confidence_threshold': 75,
                    'entry_sizes': [2, 3, 4, 5],
                    'starting_bankroll': 1000,
                    'bet_size': 50,
                    'bankroll_strategy': 'flat'
                }
            },
            {
                'name': 'confidence_based',
                'params': {
                    'confidence_threshold': 80,
                    'entry_sizes': [2, 3],
                    'starting_bankroll': 1000,
                    'bet_size': 100,
                    'bankroll_strategy': 'flat'
                }
            },
            {
                'name': 'value_based',
                'params': {
                    'ev_threshold': 10,
                    'entry_sizes': [2, 3, 4],
                    'starting_bankroll': 1000,
                    'bet_size': 50,
                    'bankroll_strategy': 'flat'
                }
            },
            {
                'name': 'composite',
                'params': {
                    'confidence_threshold': 75,
                    'ev_threshold': 5,
                    'entry_sizes': [2, 3, 4, 5],
                    'starting_bankroll': 1000,
                    'bet_size': 50,
                    'bankroll_strategy': 'flat'
                }
            }
        ]
        
        # Test each sport separately
        sports = ['NBA', 'NFL', None]  # None = both sports
        
        results = []
        
        for sport in sports:
            sport_label = sport if sport else "Both"
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Testing {sport_label} strategies")
            self.logger.info(f"{'='*60}")
            
            for strategy in strategies:
                try:
                    self.logger.info(f"\nRunning {strategy['name']} strategy for {sport_label}")
                    
                    result = self.runner.run_backtest(
                        strategy_name=strategy['name'],
                        start_date=start_str,
                        end_date=end_str,
                        sport=sport,
                        **strategy['params']
                    )
                    
                    if result:
                        # Save to database
                        backtest_id = self.runner.save_backtest_results(result)
                        
                        perf = result['performance']
                        self.logger.info(f"✅ Completed: {strategy['name']} ({sport_label})")
                        self.logger.info(f"   Win Rate: {perf['win_rate']}% | ROI: {perf['roi']}% | Profit: ${perf['total_profit']:.2f}")
                        self.logger.info(f"   Saved with ID: {backtest_id}")
                        
                        results.append({
                            'id': backtest_id,
                            'strategy': strategy['name'],
                            'sport': sport_label,
                            'result': result
                        })
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed: {strategy['name']} ({sport_label}) - {e}")
                    continue
        
        # Generate summary report
        self._generate_summary_report(results)
        
        self.logger.info("\n" + "="*60)
        self.logger.info("Weekly backtesting completed!")
        self.logger.info(f"Total strategies tested: {len(results)}")
        self.logger.info("="*60)
        
        return results
    
    def _generate_summary_report(self, results):
        """Generate a summary report of all backtests"""
        self.logger.info("\n" + "="*60)
        self.logger.info("WEEKLY BACKTEST SUMMARY")
        self.logger.info("="*60)
        
        if not results:
            self.logger.info("No results to report")
            return
        
        # Find best performers
        best_roi = max(results, key=lambda x: x['result']['performance']['roi'])
        best_win_rate = max(results, key=lambda x: x['result']['performance']['win_rate'])
        best_profit = max(results, key=lambda x: x['result']['performance']['total_profit'])
        
        self.logger.info("\n🏆 Best Performers:")
        self.logger.info(f"\nHighest ROI:")
        self.logger.info(f"  Strategy: {best_roi['strategy']} ({best_roi['sport']})")
        self.logger.info(f"  ROI: {best_roi['result']['performance']['roi']}%")
        self.logger.info(f"  Win Rate: {best_roi['result']['performance']['win_rate']}%")
        
        self.logger.info(f"\nHighest Win Rate:")
        self.logger.info(f"  Strategy: {best_win_rate['strategy']} ({best_win_rate['sport']})")
        self.logger.info(f"  Win Rate: {best_win_rate['result']['performance']['win_rate']}%")
        self.logger.info(f"  ROI: {best_win_rate['result']['performance']['roi']}%")
        
        self.logger.info(f"\nHighest Profit:")
        self.logger.info(f"  Strategy: {best_profit['strategy']} ({best_profit['sport']})")
        self.logger.info(f"  Profit: ${best_profit['result']['performance']['total_profit']:.2f}")
        self.logger.info(f"  ROI: {best_profit['result']['performance']['roi']}%")
        
        # Calculate averages
        avg_roi = sum(r['result']['performance']['roi'] for r in results) / len(results)
        avg_win_rate = sum(r['result']['performance']['win_rate'] for r in results) / len(results)
        total_profit = sum(r['result']['performance']['total_profit'] for r in results)
        
        self.logger.info(f"\n📈 Averages Across All Strategies:")
        self.logger.info(f"  Average ROI: {avg_roi:.2f}%")
        self.logger.info(f"  Average Win Rate: {avg_win_rate:.2f}%")
        self.logger.info(f"  Total Profit (all strategies): ${total_profit:.2f}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.db.close()


def main():
    """Main entry point"""
    try:
        backtester = WeeklyBacktester()
        results = backtester.run_weekly_backtests()
        return 0
    
    except Exception as e:
        logger.error(f"Error in weekly backtesting: {e}", exc_info=True)
        return 1
    
    finally:
        backtester.cleanup()


if __name__ == '__main__':
    sys.exit(main())

