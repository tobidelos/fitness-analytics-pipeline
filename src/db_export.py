import sqlite3
import pandas as pd
from sqlalchemy import create_engine, exc
from src.config import CLEAN_DATA_PATH, DB_PATH, DB_URI
from src.logger import get_logger

logger = get_logger(__name__)

def build_robust_schema(db_name: str, table_name: str = "performance_metrics"):
    """
    Creates the SQLite schema enforcing the Primary Key explicitly.
    Time Complexity: O(1)
    """
    logger.info("Validating / Building Database Schema...")
    try:
        # SQLite connect expects a string path
        con = sqlite3.connect(str(db_name))
        cursor = con.cursor()
        
        # Define Constraints
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            fecha TEXT PRIMARY KEY,
            tipo_entrenamiento TEXT,
            horario_entrenamiento TEXT,
            volumen_kg REAL,
            horas_sueno REAL,
            proteinas_g INTEGER,
            carbohidratos_g INTEGER,
            kcal_totales INTEGER,
            fuentes_principales TEXT
        )
        ''')
        con.commit()
    except sqlite3.Error as e:
        logger.error(f"Native SQLite Error creating table: {e}")
        raise
    finally:
        con.close()

def run_phase_4():
    """
    Exports data to the local SQLite Database.
    Space Complexity: O(n) for transient Parquet load.
    Time Complexity: O(n) for I/O operations.
    """
    logger.info("Initializing Phase 4: Database Export.")
    table_name = 'performance_metrics'
    
    build_robust_schema(db_name=DB_PATH, table_name=table_name)
    
    try:
        df = pd.read_parquet(CLEAN_DATA_PATH)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
    except Exception as e:
        logger.error(f"Critical failure reading Parquet or parsing dates: {e}")
        raise

    engine = create_engine(DB_URI)
    
    try:
        # Using if_exists='replace' will overwrite the table, ensuring idempotent runs
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        logger.info(f"SUCCESS: Inserted {len(df)} records into the database.")
    except exc.IntegrityError as ie:
        logger.error("INTEGRITY FAILURE: Duplicate records detected.")
        logger.debug(f"SQLAlchemy Detail: {ie}")
    except exc.OperationalError as oe:
        logger.error("OPERATIONAL FAILURE: Database or table locked.")
        logger.debug(f"SQLAlchemy Detail: {oe}")
    except Exception as general_error:
        logger.error(f"UNEXPECTED CRITICAL ERROR: {general_error}", exc_info=True)
        raise
    finally:
        engine.dispose()
