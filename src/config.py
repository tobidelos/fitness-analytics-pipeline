import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# File Paths
RAW_DATA_PATH = DATA_DIR / "raw_data.csv"
CLEAN_DATA_PATH = DATA_DIR / "clean_data.parquet"
DB_PATH = DATA_DIR / "performance_metrics.db"
DB_URI = f"sqlite:///{DB_PATH}"

# Global Parameters
N_DAYS = 180
RANDOM_SEED = 42
SLEEP_MEAN = 7.5
SLEEP_STD = 1.2
VOL_MIN = 5000
VOL_MAX = 15000
