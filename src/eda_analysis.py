import pandas as pd
from scipy import stats
from typing import Dict, Any
from src.config import CLEAN_DATA_PATH
from src.logger import get_logger

logger = get_logger(__name__)

def test_sleep_impact_on_legs(df: pd.DataFrame) -> Dict[str, Any]:
    """Tests if sleep < 6.5h affects Leg day volume using Welch's T-Test."""
    df_legs = df[df['tipo_entrenamiento'] == 'Legs'].dropna(subset=['sueno_noche_anterior'])
    
    if len(df_legs) < 2:
        return {"status": "insufficient_data"}
        
    legs_bad_sleep = df_legs[df_legs['sueno_noche_anterior'] < 6.5]['volumen_kg']
    legs_good_sleep = df_legs[df_legs['sueno_noche_anterior'] >= 6.5]['volumen_kg']
    
    if len(legs_bad_sleep) > 1 and len(legs_good_sleep) > 1:
        t_stat, p_val = stats.ttest_ind(legs_bad_sleep, legs_good_sleep, equal_var=False)
        return {
            "status": "success",
            "t_stat": t_stat,
            "p_val": p_val,
            "mean_bad": legs_bad_sleep.mean(),
            "mean_good": legs_good_sleep.mean(),
            "significant": p_val < 0.05
        }
    return {"status": "insufficient_variance"}

def test_glycogen_load_on_volume(df: pd.DataFrame) -> Dict[str, Any]:
    """Tests correlation between prior day carbs and current volume."""
    df_active = df[df['tipo_entrenamiento'] != 'Rest'].dropna(subset=['carbo_dia_anterior'])
    
    if len(df_active) < 2:
        return {"status": "insufficient_data"}
        
    var_x = df_active['carbo_dia_anterior']
    var_y = df_active['volumen_kg']
    
    corr_pearson, p_pearson = stats.pearsonr(var_x, var_y)
    corr_spearman, p_spearman = stats.spearmanr(var_x, var_y)
    
    return {
        "status": "success",
        "pearson": {"r": corr_pearson, "p_val": p_pearson},
        "spearman": {"rho": corr_spearman, "p_val": p_spearman},
        "significant": p_pearson < 0.05
    }

def run_phase_3():
    """Executes Phase 3 EDA and hypothesis testing."""
    logger.info("Initializing Phase 3: Exploratory Data Analysis (EDA)...")
    try:
        df = pd.read_parquet(CLEAN_DATA_PATH)
        df['sueno_noche_anterior'] = df['horas_sueno'].shift(1)
        df['carbo_dia_anterior'] = df['carbohidratos_g'].shift(1)
        
        # Hypothesis 1
        logger.info("Testing Hypothesis 1: Impact of Sleep on Leg Training Volume")
        h1_result = test_sleep_impact_on_legs(df)
        if h1_result.get("status") == "success":
            logger.info(f"H1 Welch T-Stat: {h1_result['t_stat']:.4f}, P-Value: {h1_result['p_val']:.4g}")
            if h1_result['significant']:
                logger.warning("H1 Conclusion: Significant drop in Leg volume due to poor sleep (<6.5h).")
            else:
                logger.info("H1 Conclusion: No statistically significant evidence of volume drop due to sleep.")
        
        # Hypothesis 2
        logger.info("Testing Hypothesis 2: Glycogen Load (Carbs N-1 vs Volume N)")
        h2_result = test_sleep_impact_on_legs(df)
        h2_result = test_glycogen_load_on_volume(df)
        if h2_result.get("status") == "success":
            logger.info(f"H2 Pearson r: {h2_result['pearson']['r']:.4f}, P-Value: {h2_result['pearson']['p_val']:.4g}")
            if h2_result['significant']:
                logger.warning("H2 Conclusion: Significant linear correlation found.")
            else:
                logger.info("H2 Conclusion: No significant linear correlation found.")
                
        logger.info("Phase 3 Complete.")
    except Exception as e:
        logger.error(f"Error during EDA Analysis: {e}", exc_info=True)
        raise
