import psycopg2
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def ensure_table_exists():
    """Ensure heart_data table exists"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS heart_data (
                        id SERIAL PRIMARY KEY,
                        age INTEGER,
                        sex INTEGER,
                        cp INTEGER,
                        trestbps INTEGER,
                        chol INTEGER,
                        fbs INTEGER,
                        restecg INTEGER,
                        thalach INTEGER,
                        exang INTEGER,
                        oldpeak FLOAT,
                        slope INTEGER,
                        ca INTEGER,
                        thal INTEGER,
                        target INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        logger.info("Verified/Created heart_data table")
    except Exception as e:
        logger.error(f"Error ensuring table exists: {e}")
        raise

def save_to_database(df):
    """Save DataFrame to database"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Clear existing data
                cur.execute("TRUNCATE TABLE heart_data RESTART IDENTITY")
                
                # Insert new data
                for _, row in df.iterrows():
                    cur.execute("""
                        INSERT INTO heart_data (
                            age, sex, cp, trestbps, chol, fbs, restecg,
                            thalach, exang, oldpeak, slope, ca, thal, target
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(row[['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                                   'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']]))
                conn.commit()
        logger.info(f"Saved {len(df)} records to database")
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        raise

def count_records():
    """Count records in database"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM heart_data")
                return cur.fetchone()[0]
    except Exception as e:
        logger.error(f"Error counting records: {e}")
        return 0