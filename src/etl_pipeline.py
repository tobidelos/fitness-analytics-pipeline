import pandas as pd
import numpy as np
from src.config import RAW_DATA_PATH, CLEAN_DATA_PATH
from src.logger import get_logger

logger = get_logger(__name__)

def unificar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes dates to ISO 8601 format."""
    df = df.copy()
    fecha_limpia = pd.to_datetime(df['fecha'], errors='coerce', dayfirst=True, format='mixed')
    df['fecha'] = fecha_limpia.dt.strftime('%Y-%m-%d')
    return df

def imputar_sueno(df: pd.DataFrame) -> pd.DataFrame:
    """Imputes missing sleep data using a 7-day rolling mean, then linear interpolation."""
    df = df.copy()
    rolling_7d = df['horas_sueno'].rolling(window=7, min_periods=1).mean()
    df['horas_sueno'] = df['horas_sueno'].fillna(rolling_7d)
    
    if df['horas_sueno'].isna().any():
        df['horas_sueno'] = df['horas_sueno'].interpolate(method='linear', limit_direction='both')
        
    df['horas_sueno'] = np.round(df['horas_sueno'], 2)
    return df

def validar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Casts specific columns to optimize memory."""
    df = df.copy()
    df['proteinas_g'] = df['proteinas_g'].astype(np.int32)
    df['carbohidratos_g'] = df['carbohidratos_g'].astype(np.int32)
    return df

def run_etl_pipeline() -> pd.DataFrame:
    """Orchestrates the data extraction, transformation, and load (ETL)."""
    logger.info("Initializing Phase 2: ETL Pipeline...")
    try:
        # Extract
        df = pd.read_csv(RAW_DATA_PATH)
        logger.info(f"Loaded raw data from {RAW_DATA_PATH}")
        
        # Transform
        df = unificar_fechas(df)
        df = imputar_sueno(df)
        df = validar_tipos(df)
        
        return df
    except Exception as e:
        logger.error(f"Error during ETL transformations: {e}", exc_info=True)
        raise

def run_phase_2():
    """Executes Phase 2 and saves to Parquet."""
    try:
        clean_df = run_etl_pipeline()
        clean_df.to_parquet(CLEAN_DATA_PATH, engine='pyarrow', index=False)
        logger.info(f"Phase 2 Complete. Cleaned data exported to '{CLEAN_DATA_PATH}'")
    except Exception as e:
        logger.error(f"Failed to export cleaned data: {e}", exc_info=True)
        raise
