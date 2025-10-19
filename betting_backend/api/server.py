
"""
Flask API Server for Betting Analysis System
Provides REST API endpoints for the dashboard frontend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
import logging
from connection import get_db_connection, handle_db_error

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow requests from the dashboard
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Helper function to convert date objects to strings for JSON serialization
def serialize_dates(obj):
    """Convert date/datetime objects to ISO format strings"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

def format_row(row):
    """Format database row for JSON response"""
    if row is None:
        return None
    return {k: serialize_dates(v) for k, v in dict(row).items()}

def format_rows(rows):
    """Format multiple database rows for JSON response"""
    return [format_row(row) for row in rows]


# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """
    Get today's predictions for NBA/NFL games
    Query params:
    - sport: 'NBA', 'NFL', or 'both' (default: 'both')
    - date: specific date in YYYY-MM-DD format (default: today)
    """
    try:
        sport = request.args.get('sport', 'both')
        target_date = request.args.get('date', date.today().isoformat())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on sport filter
        sport_filter = ""
        params = [target_date]
        
        if sport.upper() != 'BOTH':
            sport_filter = "AND g.sport = %s"
            params.append(sport.upper())
        
        query = f"""
            SELECT 
                proj.id,
                p.name as player_name,
                p.position,
                t.name as team_name,
                t.abbreviation as team_abbr,
                g.date as game_date,
                ht.name as home_team,
                ht.abbreviation as home_abbr,
                at.name as away_team,
                at.abbreviation as away_abbr,
                proj.prop_type,
                proj.projected_value,
                proj.confidence,
                proj.model_version,
                g.sport,
                proj.created_at
            FROM projections proj
            JOIN players p ON proj.player_id = p.id
            JOIN teams t ON p.team_id = t.id
            JOIN games g ON proj.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE g.date = %s 
            {sport_filter}
            AND g.status = 'scheduled'
            ORDER BY proj.confidence DESC, proj.created_at DESC
        """
        
        cursor.execute(query, params)
        predictions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'date': target_date,
            'sport': sport,
            'predictions': format_rows(predictions)
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "fetching predictions")


@app.route('/api/value-bets', methods=['GET'])
def get_value_bets():
    """
    Get current value bets (predictions with positive expected value)
    Query params:
    - sport: 'NBA', 'NFL', or 'both' (default: 'both')
    - min_confidence: minimum confidence threshold (default: 60)
    - min_ev: minimum expected value percentage (default: 5)
    """
    try:
        sport = request.args.get('sport', 'both')
        min_confidence = float(request.args.get('min_confidence', 60))
        min_ev = float(request.args.get('min_ev', 5))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sport_filter = ""
        params = [date.today().isoformat(), min_confidence]
        
        if sport.upper() != 'BOTH':
            sport_filter = "AND g.sport = %s"
            params.append(sport.upper())
        
        # Value bets are projections with high confidence for upcoming games
        # In a real system, you'd compare against market lines to calculate EV
        # For now, we'll use confidence as a proxy for value
        query = f"""
            SELECT 
                proj.id,
                p.name as player_name,
                p.position,
                t.name as team_name,
                t.abbreviation as team_abbr,
                g.date as game_date,
                g.time as game_time,
                ht.name as home_team,
                ht.abbreviation as home_abbr,
                at.name as away_team,
                at.abbreviation as away_abbr,
                proj.prop_type,
                proj.projected_value,
                proj.confidence,
                proj.model_version,
                g.sport,
                -- Placeholder EV calculation (confidence - 50) as percentage
                (proj.confidence - 50) as expected_value
            FROM projections proj
            JOIN players p ON proj.player_id = p.id
            JOIN teams t ON p.team_id = t.id
            JOIN games g ON proj.game_id = g.id
            JOIN teams ht ON g.home_team_id = ht.id
            JOIN teams at ON g.away_team_id = at.id
            WHERE g.date >= %s
            AND g.status = 'scheduled'
            AND proj.confidence >= %s
            {sport_filter}
            ORDER BY proj.confidence DESC, g.date ASC
            LIMIT 50
        """
        
        cursor.execute(query, params)
        value_bets = cursor.fetchall()
        
        # Filter by minimum EV
        filtered_bets = [bet for bet in value_bets if bet['expected_value'] >= min_ev]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(filtered_bets),
            'filters': {
                'sport': sport,
                'min_confidence': min_confidence,
                'min_ev': min_ev
            },
            'value_bets': format_rows(filtered_bets)
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "fetching value bets")


@app.route('/api/bets', methods=['GET'])
def get_bets():
    """
    Get user's bet history
    Query params:
    - status: 'pending', 'win', 'loss', 'push', 'cancelled', or 'all' (default: 'all')
    - sport: 'NBA', 'NFL', or 'both' (default: 'both')
    - limit: number of results (default: 100)
    - offset: pagination offset (default: 0)
    """
    try:
        status = request.args.get('status', 'all')
        sport = request.args.get('sport', 'both')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        status_filter = "" if status == 'all' else "WHERE outcome = %s"
        
        query = f"""
            SELECT 
                id,
                date,
                entry_type,
                props,
                stake,
                odds,
                outcome,
                pnl,
                notes,
                created_at,
                updated_at
            FROM bets
            {status_filter}
            ORDER BY date DESC, created_at DESC
            LIMIT %s OFFSET %s
        """
        
        params = [status] if status != 'all' else []
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        bets = cursor.fetchall()
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total FROM bets
            {status_filter}
        """
        count_params = [status] if status != 'all' else []
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(bets),
            'total': total,
            'filters': {
                'status': status,
                'sport': sport,
                'limit': limit,
                'offset': offset
            },
            'bets': format_rows(bets)
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "fetching bets")


@app.route('/api/bets', methods=['POST'])
def add_bet():
    """
    Add a new bet to the database
    Expected JSON body:
    {
        "date": "2024-10-19",
        "entry_type": "3-pick",
        "props": [...],
        "stake": 10.00,
        "odds": 6.0,
        "notes": "Optional notes"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'entry_type', 'props', 'stake']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO bets (date, entry_type, props, stake, odds, outcome, notes)
            VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s)
            RETURNING id, date, entry_type, props, stake, odds, outcome, pnl, notes, created_at
        """
        
        import json
        cursor.execute(query, (
            data['date'],
            data['entry_type'],
            json.dumps(data['props']),
            data['stake'],
            data.get('odds'),
            data.get('outcome', 'pending'),
            data.get('notes')
        ))
        
        new_bet = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"New bet added: ID {new_bet['id']}")
        
        return jsonify({
            'success': True,
            'message': 'Bet added successfully',
            'bet': format_row(new_bet)
        }), 201
        
    except Exception as e:
        return handle_db_error(e, "adding bet")


@app.route('/api/bets/<int:bet_id>', methods=['PUT'])
def update_bet(bet_id):
    """
    Update a bet's status and outcome
    Expected JSON body:
    {
        "outcome": "win" | "loss" | "push" | "cancelled",
        "pnl": 10.50,
        "notes": "Optional notes"
    }
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if 'outcome' in data:
            update_fields.append("outcome = %s")
            params.append(data['outcome'])
        
        if 'pnl' in data:
            update_fields.append("pnl = %s")
            params.append(data['pnl'])
        
        if 'notes' in data:
            update_fields.append("notes = %s")
            params.append(data['notes'])
        
        if not update_fields:
            return jsonify({
                'success': False,
                'error': 'No fields to update'
            }), 400
        
        params.append(bet_id)
        
        query = f"""
            UPDATE bets 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, date, entry_type, props, stake, odds, outcome, pnl, notes, created_at, updated_at
        """
        
        cursor.execute(query, params)
        updated_bet = cursor.fetchone()
        
        if not updated_bet:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Bet with ID {bet_id} not found'
            }), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Bet updated: ID {bet_id}")
        
        return jsonify({
            'success': True,
            'message': 'Bet updated successfully',
            'bet': format_row(updated_bet)
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "updating bet")


@app.route('/api/bets/<int:bet_id>', methods=['DELETE'])
def delete_bet(bet_id):
    """Delete a bet from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if bet exists
        cursor.execute("SELECT id FROM bets WHERE id = %s", (bet_id,))
        bet = cursor.fetchone()
        
        if not bet:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Bet with ID {bet_id} not found'
            }), 404
        
        # Delete the bet
        cursor.execute("DELETE FROM bets WHERE id = %s", (bet_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Bet deleted: ID {bet_id}")
        
        return jsonify({
            'success': True,
            'message': 'Bet deleted successfully',
            'deleted_id': bet_id
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "deleting bet")


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Get performance analytics data
    Query params:
    - period: 'week', 'month', 'season', or 'all' (default: 'all')
    """
    try:
        period = request.args.get('period', 'all')
        
        # Calculate date range based on period
        date_filter = ""
        if period == 'week':
            date_filter = f"WHERE date >= '{(date.today() - timedelta(days=7)).isoformat()}'"
        elif period == 'month':
            date_filter = f"WHERE date >= '{(date.today() - timedelta(days=30)).isoformat()}'"
        elif period == 'season':
            # Approximate season as last 6 months
            date_filter = f"WHERE date >= '{(date.today() - timedelta(days=180)).isoformat()}'"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Overall statistics
        stats_query = f"""
            SELECT 
                COUNT(*) as total_bets,
                COUNT(CASE WHEN outcome = 'pending' THEN 1 END) as active_bets,
                COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
                COUNT(CASE WHEN outcome = 'loss' THEN 1 END) as losses,
                COUNT(CASE WHEN outcome = 'push' THEN 1 END) as pushes,
                COALESCE(SUM(stake), 0) as total_staked,
                COALESCE(SUM(CASE WHEN outcome != 'pending' THEN pnl ELSE 0 END), 0) as total_pnl,
                COALESCE(AVG(stake), 0) as avg_stake
            FROM bets
            {date_filter}
        """
        
        cursor.execute(stats_query)
        stats = cursor.fetchone()
        
        # Calculate derived metrics
        completed_bets = stats['wins'] + stats['losses'] + stats['pushes']
        win_rate = (stats['wins'] / completed_bets * 100) if completed_bets > 0 else 0
        roi = (stats['total_pnl'] / stats['total_staked'] * 100) if stats['total_staked'] > 0 else 0
        
        # Performance by entry type
        entry_type_query = f"""
            SELECT 
                entry_type,
                COUNT(*) as total,
                COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
                COALESCE(SUM(CASE WHEN outcome != 'pending' THEN pnl ELSE 0 END), 0) as pnl
            FROM bets
            {date_filter}
            GROUP BY entry_type
            ORDER BY entry_type
        """
        
        cursor.execute(entry_type_query)
        by_entry_type = cursor.fetchall()
        
        # Performance by prop type (extract from JSONB props)
        prop_type_query = f"""
            SELECT 
                prop->>'propType' as prop_type,
                COUNT(*) as total,
                COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins
            FROM bets, jsonb_array_elements(props) as prop
            {date_filter}
            GROUP BY prop->>'propType'
            ORDER BY total DESC
            LIMIT 10
        """
        
        cursor.execute(prop_type_query)
        by_prop_type = cursor.fetchall()
        
        # Daily performance trend (last 30 days)
        trend_query = """
            SELECT 
                date,
                COUNT(*) as bets,
                COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
                COALESCE(SUM(CASE WHEN outcome != 'pending' THEN pnl ELSE 0 END), 0) as daily_pnl
            FROM bets
            WHERE date >= %s AND outcome != 'pending'
            GROUP BY date
            ORDER BY date DESC
            LIMIT 30
        """
        
        cursor.execute(trend_query, [(date.today() - timedelta(days=30)).isoformat()])
        daily_trend = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'period': period,
            'overall': {
                'total_bets': stats['total_bets'],
                'active_bets': stats['active_bets'],
                'completed_bets': completed_bets,
                'wins': stats['wins'],
                'losses': stats['losses'],
                'pushes': stats['pushes'],
                'win_rate': round(win_rate, 2),
                'total_staked': float(stats['total_staked']),
                'total_pnl': float(stats['total_pnl']),
                'roi': round(roi, 2),
                'avg_stake': float(stats['avg_stake'])
            },
            'by_entry_type': format_rows(by_entry_type),
            'by_prop_type': format_rows(by_prop_type),
            'daily_trend': format_rows(daily_trend)
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "fetching analytics")


@app.route('/api/backtest-results', methods=['GET'])
def get_backtest_results():
    """
    Get backtesting results
    Note: This is a placeholder as backtesting tables aren't fully defined yet
    """
    try:
        # For now, return a placeholder response
        # In a complete system, you'd query backtesting-specific tables
        return jsonify({
            'success': True,
            'message': 'Backtesting results endpoint - implement based on your backtesting schema',
            'results': []
        }), 200
        
    except Exception as e:
        return handle_db_error(e, "fetching backtest results")


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    logger.info(f"Starting Flask API server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
