import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.config import N_DAYS, RANDOM_SEED, RAW_DATA_PATH, SLEEP_MEAN, SLEEP_STD, VOL_MIN, VOL_MAX
from src.logger import get_logger

logger = get_logger(__name__)

def generate_synthetic_data() -> pd.DataFrame:
    """
    Generates a synthetic tabular dataset with historical fitness records.
    
    Time Complexity: O(1) in terms of Python loops, relies on vectorization (O(n) internally in C).
    Space Complexity: O(n) where n is N_DAYS.
    """
    logger.info("Initializing Phase 1: Synthetic Data Generation...")
    np.random.seed(RANDOM_SEED)
    
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=N_DAYS-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df = pd.DataFrame({'fecha': dates})
    
    # 1. Dates (Vectorized with noise)
    noise_mask = np.random.rand(N_DAYS) < 0.03
    dates_normal = df['fecha'].dt.strftime('%Y-%m-%d')
    dates_noise = df['fecha'].dt.strftime('%d/%m/%Y')
    df['fecha'] = np.where(noise_mask, dates_noise, dates_normal)
    
    # 2. Training Type (6 on, 1 off)
    cycle = ['Push', 'Pull', 'Legs', 'Push', 'Pull', 'Legs', 'Rest']
    training_types = np.tile(cycle, int(np.ceil(N_DAYS / len(cycle))))[:N_DAYS]
    df['tipo_entrenamiento'] = training_types
    
    # 3. Training Schedule (85% Morning, 15% Afternoon)
    df['horario_entrenamiento'] = np.random.choice(
        ['Mañana', 'Tarde'], 
        size=N_DAYS, 
        p=[0.85, 0.15]
    )
    
    # 4. Volume in KG
    vol_raw = np.random.uniform(VOL_MIN, VOL_MAX, size=N_DAYS)
    df['volumen_kg'] = np.where(df['tipo_entrenamiento'] == 'Rest', 0.0, np.round(vol_raw, 2))
    
    # 5. Sleep Hours (with 5% NaN)
    sleep = np.random.normal(loc=SLEEP_MEAN, scale=SLEEP_STD, size=N_DAYS)
    sleep = np.clip(sleep, 3.0, 12.0)
    nan_mask = np.random.rand(N_DAYS) < 0.05
    sleep[nan_mask] = np.nan
    df['horas_sueno'] = np.round(sleep, 2)
    
    # 6. Macros and Calories
    df['proteinas_g'] = np.random.randint(140, 201, size=N_DAYS)
    df['carbohidratos_g'] = np.random.randint(250, 451, size=N_DAYS)
    fats_g = np.random.randint(60, 100, size=N_DAYS)
    df['kcal_totales'] = (df['proteinas_g'] * 4) + (df['carbohidratos_g'] * 4) + (fats_g * 9)
    
    # 7. Main Food Sources
    valid_sources = [
        'Pollo, Arroz, Yogur Casero', 
        'Carne Magra, Papa, Avena', 
        'Huevo, Fideos, Yogur Casero'
    ]
    df['fuentes_principales'] = np.random.choice(valid_sources, size=N_DAYS)
    
    return df

def run_phase_1():
    """Executes Phase 1 and saves the data to the configured path."""
    try:
        df = generate_synthetic_data()
        df.to_csv(RAW_DATA_PATH, index=False)
        logger.info(f"Phase 1 Complete. Dataset exported to '{RAW_DATA_PATH}'")
        logger.debug(f"Data Preview:\n{df.head(3)}")
    except Exception as e:
        logger.error(f"Failed to generate and export data: {e}", exc_info=True)
        raise
