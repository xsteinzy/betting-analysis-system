
"""
Value Finder - Compare predictions to betting lines and identify value bets
"""
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.logger import setup_logger
from models.nba.config import VALUE_BET_CONFIG

logger = setup_logger('value_finder')


class ValueFinder:
    """Identify value bets by comparing predictions to betting lines"""
    
    def __init__(self):
        self.config = VALUE_BET_CONFIG
    
    def calculate_expected_value(self, predicted_value: float, betting_line: float,
                                confidence: float, odds: float = -110) -> Dict[str, Any]:
        """
        Calculate expected value for a bet
        
        Args:
            predicted_value: Model's predicted value
            betting_line: Bookmaker's line
            confidence: Confidence score (0-100)
            odds: American odds (default -110)
            
        Returns:
            Dictionary with EV calculation details
        """
        try:
            # Calculate edge (difference between prediction and line)
            edge = predicted_value - betting_line
            edge_pct = (edge / betting_line * 100) if betting_line != 0 else 0
            
            # Estimate win probability based on edge and confidence
            # This is a simplified model - can be improved with historical data
            base_probability = 0.5  # 50% baseline for prop bets
            
            # Adjust probability based on edge
            edge_adjustment = edge * 0.02  # Each point of edge = 2% probability shift
            
            # Adjust based on confidence
            confidence_multiplier = confidence / 100
            
            win_probability = base_probability + (edge_adjustment * confidence_multiplier)
            win_probability = max(0.1, min(0.9, win_probability))  # Bound between 10-90%
            
            # Convert American odds to decimal
            if odds < 0:
                decimal_odds = 1 + (100 / abs(odds))
            else:
                decimal_odds = 1 + (odds / 100)
            
            # Calculate EV
            # EV = (Win Probability × Payout) - (Loss Probability × Stake)
            # Assuming stake of $100
            stake = 100
            payout = stake * (decimal_odds - 1)
            loss = stake
            
            ev = (win_probability * payout) - ((1 - win_probability) * loss)
            ev_pct = (ev / stake) * 100
            
            return {
                'edge': round(edge, 2),
                'edge_pct': round(edge_pct, 1),
                'win_probability': round(win_probability * 100, 1),
                'expected_value': round(ev, 2),
                'ev_pct': round(ev_pct, 1),
                'decimal_odds': round(decimal_odds, 2),
                'suggested_stake': stake
            }
            
        except Exception as e:
            logger.error(f"Error calculating EV: {e}")
            return None
    
    def evaluate_bet(self, prediction: Dict[str, Any], betting_line: float,
                    odds: float = -110, bet_direction: str = 'over') -> Dict[str, Any]:
        """
        Evaluate if a bet has value
        
        Args:
            prediction: Prediction dictionary from predictor
            betting_line: Bookmaker's line
            odds: American odds
            bet_direction: 'over' or 'under'
            
        Returns:
            Dictionary with bet evaluation
        """
        try:
            predicted_value = prediction['predicted_value']
            confidence = prediction['confidence_score']
            
            # Adjust prediction based on bet direction
            if bet_direction.lower() == 'under':
                # For under bets, flip the comparison
                edge = betting_line - predicted_value
                favorable = edge > 0
            else:
                # For over bets
                edge = predicted_value - betting_line
                favorable = edge > 0
            
            # Calculate EV
            ev_calc = self.calculate_expected_value(
                predicted_value, betting_line, confidence, odds
            )
            
            if ev_calc is None:
                return None
            
            # Determine value rating
            ev_pct = ev_calc['ev_pct']
            
            if ev_pct > self.config['strong_value_threshold']:
                value_rating = 'Strong Value'
                recommendation = 'BET'
            elif ev_pct > self.config['moderate_value_threshold']:
                value_rating = 'Moderate Value'
                recommendation = 'BET' if confidence >= self.config['min_confidence_for_bet'] else 'PASS'
            elif ev_pct > self.config['slight_value_threshold']:
                value_rating = 'Slight Value'
                recommendation = 'PASS'
            else:
                value_rating = 'No Value'
                recommendation = 'PASS'
            
            # Additional checks
            if abs(edge) < self.config['min_edge_for_recommendation']:
                recommendation = 'PASS'
                value_rating = 'Edge Too Small'
            
            if confidence < self.config['min_confidence_for_bet']:
                if recommendation == 'BET':
                    recommendation = 'PASS (Low Confidence)'
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                prediction, betting_line, edge, confidence, 
                ev_pct, bet_direction
            )
            
            return {
                'player_name': prediction['player_name'],
                'prop_type': prediction['prop_type'],
                'game_date': prediction['game_date'],
                'predicted_value': predicted_value,
                'betting_line': betting_line,
                'bet_direction': bet_direction.upper(),
                'odds': odds,
                'edge': round(edge, 2),
                'confidence': confidence,
                'ev_pct': ev_pct,
                'win_probability': ev_calc['win_probability'],
                'value_rating': value_rating,
                'recommendation': recommendation,
                'reasoning': reasoning,
                'prediction_range': f"{prediction['prediction_low']} - {prediction['prediction_high']}",
                'model_version': prediction['model_version'],
                'evaluated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating bet: {e}")
            return None
    
    def _generate_reasoning(self, prediction: Dict, betting_line: float,
                          edge: float, confidence: float, ev_pct: float,
                          bet_direction: str) -> str:
        """Generate human-readable reasoning for the bet evaluation"""
        player_name = prediction['player_name']
        prop_type = prediction['prop_type']
        predicted_value = prediction['predicted_value']
        
        reasoning_parts = []
        
        # Edge explanation
        if edge > 0:
            reasoning_parts.append(
                f"Model projects {predicted_value} {prop_type}, "
                f"line is {betting_line}, giving a +{abs(edge):.1f} point edge."
            )
        else:
            reasoning_parts.append(
                f"Model projects {predicted_value} {prop_type}, "
                f"line is {betting_line}, showing a -{abs(edge):.1f} point disadvantage."
            )
        
        # Confidence explanation
        if confidence >= 80:
            reasoning_parts.append(f"High confidence ({confidence}%) based on model agreement and data quality.")
        elif confidence >= 60:
            reasoning_parts.append(f"Moderate confidence ({confidence}%).")
        else:
            reasoning_parts.append(f"Low confidence ({confidence}%) - limited data or model disagreement.")
        
        # EV explanation
        if ev_pct > 5:
            reasoning_parts.append(f"Strong positive expected value (+{ev_pct:.1f}%).")
        elif ev_pct > 2:
            reasoning_parts.append(f"Moderate positive expected value (+{ev_pct:.1f}%).")
        elif ev_pct > 0:
            reasoning_parts.append(f"Slight positive expected value (+{ev_pct:.1f}%).")
        else:
            reasoning_parts.append(f"Negative expected value ({ev_pct:.1f}%).")
        
        # Additional context
        pred_range = prediction.get('prediction_low', 0)
        pred_range_high = prediction.get('prediction_high', 0)
        
        if bet_direction.lower() == 'over':
            if betting_line < pred_range:
                reasoning_parts.append(f"Line is below predicted range ({pred_range:.1f}-{pred_range_high:.1f}).")
        else:
            if betting_line > pred_range_high:
                reasoning_parts.append(f"Line is above predicted range ({pred_range:.1f}-{pred_range_high:.1f}).")
        
        return " ".join(reasoning_parts)
    
    def find_best_values(self, predictions: List[Dict[str, Any]], 
                        betting_lines: Dict[str, Dict[str, float]],
                        min_confidence: float = None,
                        top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Find best value bets from a list of predictions
        
        Args:
            predictions: List of prediction dictionaries
            betting_lines: Dictionary of betting lines
                          Format: {player_id: {prop_type: line_value}}
            min_confidence: Minimum confidence threshold
            top_n: Number of top value bets to return
            
        Returns:
            List of best value bets sorted by EV
        """
        if min_confidence is None:
            min_confidence = self.config['min_confidence_for_bet']
        
        try:
            value_bets = []
            
            for pred in predictions:
                player_id = pred['player_id']
                prop_type = pred['prop_type']
                
                # Check if we have a betting line for this player/prop
                if player_id not in betting_lines:
                    continue
                if prop_type not in betting_lines[player_id]:
                    continue
                
                betting_line = betting_lines[player_id][prop_type]
                
                # Evaluate both over and under
                over_eval = self.evaluate_bet(pred, betting_line, bet_direction='over')
                under_eval = self.evaluate_bet(pred, betting_line, bet_direction='under')
                
                if over_eval and over_eval['confidence'] >= min_confidence:
                    value_bets.append(over_eval)
                
                if under_eval and under_eval['confidence'] >= min_confidence:
                    value_bets.append(under_eval)
            
            # Sort by EV percentage
            value_bets.sort(key=lambda x: x['ev_pct'], reverse=True)
            
            # Filter to recommendations
            recommended_bets = [bet for bet in value_bets if bet['recommendation'] == 'BET']
            
            logger.info(f"Found {len(recommended_bets)} recommended value bets out of {len(value_bets)} evaluated")
            
            return recommended_bets[:top_n]
            
        except Exception as e:
            logger.error(f"Error finding best values: {e}")
            return []
    
    def compare_to_line(self, prediction: Dict[str, Any], 
                       betting_line: float) -> str:
        """
        Simple comparison of prediction to betting line
        
        Args:
            prediction: Prediction dictionary
            betting_line: Betting line value
            
        Returns:
            Human-readable comparison string
        """
        predicted_value = prediction['predicted_value']
        edge = predicted_value - betting_line
        
        if abs(edge) < 0.5:
            return f"Very close to line (difference: {edge:+.1f})"
        elif edge > 2:
            return f"Well above line (+{edge:.1f} - STRONG OVER)"
        elif edge > 1:
            return f"Above line (+{edge:.1f} - OVER)"
        elif edge < -2:
            return f"Well below line ({edge:.1f} - STRONG UNDER)"
        elif edge < -1:
            return f"Below line ({edge:.1f} - UNDER)"
        else:
            return f"Close to line ({edge:+.1f})"


def main():
    """Example usage"""
    # Example prediction
    example_prediction = {
        'player_id': 123,
        'player_name': 'LeBron James',
        'prop_type': 'points',
        'game_date': '2024-10-19',
        'predicted_value': 28.5,
        'prediction_low': 24.0,
        'prediction_high': 33.0,
        'confidence_score': 78.5,
        'model_version': '1.0.0'
    }
    
    # Example betting line
    betting_line = 25.5
    odds = -110
    
    # Create value finder
    value_finder = ValueFinder()
    
    # Evaluate over bet
    over_eval = value_finder.evaluate_bet(
        example_prediction, betting_line, odds, 'over'
    )
    
    print("\n" + "="*60)
    print("VALUE BET ANALYSIS")
    print("="*60)
    print(f"Player: {over_eval['player_name']}")
    print(f"Prop: {over_eval['prop_type']}")
    print(f"Predicted: {over_eval['predicted_value']}")
    print(f"Line: {over_eval['betting_line']}")
    print(f"Edge: {over_eval['edge']:+.1f}")
    print(f"Confidence: {over_eval['confidence']}%")
    print(f"Expected Value: {over_eval['ev_pct']:+.1f}%")
    print(f"Win Probability: {over_eval['win_probability']}%")
    print(f"Value Rating: {over_eval['value_rating']}")
    print(f"Recommendation: {over_eval['recommendation']}")
    print(f"\nReasoning: {over_eval['reasoning']}")
    print("="*60)


if __name__ == '__main__':
    main()
