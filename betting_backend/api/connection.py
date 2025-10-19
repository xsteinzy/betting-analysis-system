
"""
Database connection utilities for the API server
Provides simple connection management for PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
from flask import jsonify

load_dotenv()
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Create and return a database connection
    Uses environment variables for configuration
    """
    try:
        # Try DATABASE_URL first (used by Render.com and other platforms)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Handle Render.com's postgres:// vs postgresql:// URL scheme
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
        else:
            # Fall back to individual environment variables
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'betting_analysis'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
        
        logger.debug("Database connection established")
        return conn
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def handle_db_error(error, operation):
    """
    Handle database errors consistently
    Returns a Flask JSON response
    """
    logger.error(f"Error {operation}: {error}")
    return jsonify({
        'success': False,
        'error': f'Database error while {operation}',
        'message': str(error)
    }), 500


def test_connection():
    """
    Test the database connection
    Returns True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


if __name__ == '__main__':
    # Test the connection when run directly
    print("Testing database connection...")
    if test_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed. Check your environment variables.")
