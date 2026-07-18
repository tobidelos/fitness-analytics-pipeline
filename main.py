import time
from src.logger import get_logger
from src.data_generator import run_phase_1
from src.etl_pipeline import run_phase_2
from src.eda_analysis import run_phase_3
from src.db_export import run_phase_4

logger = get_logger("main_orchestrator")

def run_pipeline():
    """Runs the complete data pipeline sequence."""
    logger.info("=== STARTING FITNESS ETL PIPELINE ===")
    start_time = time.time()
    
    try:
        # Phase 1: Data Generation
        run_phase_1()
        
        # Phase 2: ETL
        run_phase_2()
        
        # Phase 3: EDA
        run_phase_3()
        
        # Phase 4: DB Export
        run_phase_4()
        
        elapsed = time.time() - start_time
        logger.info(f"=== PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s ===")
        
    except Exception as e:
        logger.error(f"Pipeline failed critically: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
