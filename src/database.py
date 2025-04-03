import os
import psycopg2
from psycopg2 import sql, extras
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import logging
from contextlib import contextmanager

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def ensure_table_exists():
    """Create the heart_disease table if it doesn't exist"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS heart_disease (
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
        target INTEGER
    );
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
        logger.info("Ensured heart_disease table exists")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise

def clear_existing_data():
    """Delete all existing data from the heart_disease table"""
    ensure_table_exists()
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE heart_disease RESTART IDENTITY;")
                conn.commit()
        logger.info("Cleared existing data from heart_disease table")
    except Exception as e:
        logger.error(f"Error clearing existing data: {e}")
        raise

def convert_numpy_types(value):
    """Convert numpy types to native Python types"""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer)):
        return int(value)
    elif isinstance(value, (np.floating)):
        return float(value)
    return value

def save_to_database(df):
    """Save DataFrame to PostgreSQL database, replacing existing data"""
    ensure_table_exists()
    
    try:
        # First clear existing data
        clear_existing_data()
        
        # Prepare data for insertion
        df = df.where(pd.notnull(df), None)  # Convert NaN to None
        records = df.to_dict('records')
        
        # Convert numpy types to native Python types
        for record in records:
            for key, value in record.items():
                record[key] = convert_numpy_types(value)
        
        # Insert data using execute_batch for better performance
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                columns = df.columns.tolist()
                insert_sql = sql.SQL(
                    "INSERT INTO heart_disease ({}) VALUES ({})"
                ).format(
                    sql.SQL(',').join(map(sql.Identifier, columns)),
                    sql.SQL(',').join(sql.Placeholder() * len(columns))
                )
                
                extras.execute_batch(cursor, insert_sql, records)
                conn.commit()
        
        logger.info(f"Saved {len(records)} records to database")
        return True
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        raise

def load_from_database():
    """Load all data from PostgreSQL database"""
    ensure_table_exists()
    try:
        with get_db_connection() as conn:
            query = "SELECT * FROM heart_disease;"
            df = pd.read_sql(query, conn)
        logger.info(f"Loaded {len(df)} records from database")
        return df
    except Exception as e:
        logger.error(f"Error loading from database: {e}")
        raise

def count_records():
    """Count number of records in the table"""
    ensure_table_exists()
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM heart_disease;")
                count = cursor.fetchone()[0]
        logger.info(f"Counted {count} records in database")
        return count
    except Exception as e:
        logger.error(f"Error counting records: {e}")
        raise