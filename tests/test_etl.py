import pandas as pd
import numpy as np
import pytest
from src.etl_pipeline import unificar_fechas, imputar_sueno, validar_tipos

def test_unificar_fechas():
    # Setup test dataframe with mixed and bad dates
    df = pd.DataFrame({
        'fecha': ['2023-01-01', '15/01/2023', 'invalid_date']
    })
    
    result_df = unificar_fechas(df)
    
    assert result_df['fecha'].iloc[0] == '2023-01-01'
    assert result_df['fecha'].iloc[1] == '2023-01-15'
    assert pd.isna(result_df['fecha'].iloc[2])

def test_imputar_sueno():
    # Setup with nans at beginning, middle, and end
    df = pd.DataFrame({
        'horas_sueno': [np.nan, 8.0, 7.0, np.nan, 6.0]
    })
    
    result_df = imputar_sueno(df)
    
    # Assert no nans remain
    assert not result_df['horas_sueno'].isna().any()
    
    # Assert specific imputations (first nan should interpolate towards 8.0)
    assert result_df['horas_sueno'].iloc[0] == 8.0
    
    # Third item is 7.0, so rolling mean for 4th item (using last 7 days) 
    # would be mean(8.0, 7.0) = 7.5
    assert result_df['horas_sueno'].iloc[3] == 7.5

def test_validar_tipos():
    df = pd.DataFrame({
        'proteinas_g': [150.5, 200.1],
        'carbohidratos_g': ['300', '400']
    })
    
    result_df = validar_tipos(df)
    
    # Assert types are int32
    assert result_df['proteinas_g'].dtype == np.int32
    assert result_df['carbohidratos_g'].dtype == np.int32
    
    # Assert values truncated/parsed correctly
    assert result_df['proteinas_g'].iloc[0] == 150
    assert result_df['carbohidratos_g'].iloc[0] == 300
