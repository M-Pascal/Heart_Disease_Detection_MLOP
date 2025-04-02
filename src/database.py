import os
import psycopg2
from psycopg2 import sql
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

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
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        raise
    finally:
        if conn:
            conn.close()

def clear_existing_data():
    """Delete all existing data from the heart_disease table"""
    ensure_table_exists()
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE heart_disease RESTART IDENTITY;")
            conn.commit()
    except Exception as e:
        print(f"Error clearing existing data: {e}")
        raise
    finally:
        if conn:
            conn.close()

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
    conn = None
    try:
        # First clear existing data
        clear_existing_data()
        
        # Then insert new data
        conn = get_connection()
        with conn.cursor() as cursor:
            # Convert DataFrame to list of tuples with native Python types
            data = []
            for row in df.to_numpy():
                converted_row = [convert_numpy_types(x) for x in row]
                data.append(tuple(converted_row))
            
            # Create the SQL insert statement
            columns = sql.SQL(',').join(
                sql.Identifier(col) for col in df.columns
            )
            values = sql.SQL(',').join(sql.Placeholder() * len(df.columns))
            query = sql.SQL(
                "INSERT INTO heart_disease ({}) VALUES ({});"
            ).format(columns, values)
            
            # Execute the query for each row
            cursor.executemany(query, data)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error saving to database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def load_from_database():
    """Load all data from PostgreSQL database"""
    ensure_table_exists()
    conn = None
    try:
        conn = get_connection()
        query = "SELECT * FROM heart_disease;"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error loading from database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def count_records():
    """Count number of records in the table"""
    ensure_table_exists()
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM heart_disease;")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print(f"Error counting records: {e}")
        raise
    finally:
        if conn:
            conn.close()