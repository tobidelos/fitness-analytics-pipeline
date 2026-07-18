import sys
from pathlib import Path

# Ensure src module can be imported when running via streamlit
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from src.config import DB_URI

# Page Configuration - Clean, no emojis
st.set_page_config(
    page_title="Performance Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Injection
st.markdown("""
    <style>
    /* Typography overrides for a sleek, corporate feel */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 300;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    
    /* Sleek Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 400;
        color: #1f77b4; /* Muted corporate blue */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #7f8c8d; /* Subtle gray */
    }
    
    /* Clean up the Streamlit UI chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    """Loads and caches data from the SQLite database."""
    try:
        engine = create_engine(DB_URI)
        query = "SELECT * FROM performance_metrics"
        df = pd.read_sql(query, engine)
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except Exception as e:
        st.error(f"System Error: Unable to establish database connection. Details: {e}")
        return pd.DataFrame()

def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders the sidebar and applies selected filters to the dataframe."""
    st.sidebar.markdown("### Filtering Controls")
    
    # Date Range
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    selected_dates = st.sidebar.date_input(
        "Observation Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Training Types
    types = sorted(df['tipo_entrenamiento'].unique().tolist())
    selected_types = st.sidebar.multiselect(
        "Training Classifications",
        options=types,
        default=types
    )
    
    # Methodology Expander in Sidebar
    with st.sidebar.expander("Methodology & Notes"):
        st.markdown("""
        **Data Processing Pipeline:**
        1. **Extraction**: Automated syntethic ingestion.
        2. **Transformation**: Missing sleep values imputed via 7-day rolling mean (pandas). Dates coerced to ISO-8601.
        3. **Storage**: Columnar Parquet -> SQLite Transactional DB.
        
        *Confidence Interval*: 95% for statistical tests (Welch, Pearson).
        """)

    # Apply filters
    if len(selected_dates) == 2:
        mask = (
            (df['fecha'].dt.date >= selected_dates[0]) & 
            (df['fecha'].dt.date <= selected_dates[1]) &
            (df['tipo_entrenamiento'].isin(selected_types))
        )
        return df.loc[mask]
    return df

def render_overview_tab(df: pd.DataFrame):
    """Renders the primary KPIs and volume analysis."""
    # Top Level Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", f"{len(df[df['tipo_entrenamiento'] != 'Rest']):,}")
    with col2:
        avg_vol = df[df['tipo_entrenamiento'] != 'Rest']['volumen_kg'].mean()
        st.metric("Avg Active Volume", f"{avg_vol:,.0f} kg")
    with col3:
        avg_sleep = df['horas_sueno'].mean()
        st.metric("Avg Sleep Duration", f"{avg_sleep:.1f} hrs")
    with col4:
        avg_kcal = df['kcal_totales'].mean()
        st.metric("Avg Caloric Intake", f"{avg_kcal:,.0f} kcal")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Volume Chart
    st.markdown("#### Longitudinal Volume Distribution")
    
    # Custom color mapping for corporate feel
    color_map = {
        'Push': '#2c3e50', # Dark Blue
        'Pull': '#34495e', # Grayish Blue
        'Legs': '#16a085', # Teal/Green
        'Rest': '#bdc3c7'  # Light Gray
    }
    
    fig = px.bar(
        df.sort_values('fecha'),
        x='fecha', 
        y='volumen_kg', 
        color='tipo_entrenamiento',
        color_discrete_map=color_map,
        labels={'fecha': '', 'volumen_kg': 'Volume (KG)', 'tipo_entrenamiento': 'Classification'}
    )
    
    # Minimalist chart styling
    fig.update_layout(
        template="simple_white",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_correlations_tab(df: pd.DataFrame):
    """Renders the statistical correlation analysis."""
    st.markdown("#### Multivariate Impact Analysis")
    st.write(
        "This scatter matrix evaluates the relationship between recovery metrics (sleep) "
        "and physical output (volume), sized by nutritional intake (calories). "
        "Ordinary Least Squares (OLS) regression highlights the statistical trend."
    )
    
    df_active = df[df['tipo_entrenamiento'] != 'Rest'].copy()
    
    if len(df_active) < 3:
        st.info("Insufficient active days to compute correlations.")
        return
        
    color_map = {'Push': '#2c3e50', 'Pull': '#34495e', 'Legs': '#16a085'}
    
    fig = px.scatter(
        df_active, 
        x='horas_sueno', 
        y='volumen_kg',
        color='tipo_entrenamiento', 
        size='kcal_totales',
        color_discrete_map=color_map,
        trendline="ols",
        trendline_scope="overall", # Single trendline for all active days
        labels={
            'horas_sueno': 'Sleep Duration (Hours)', 
            'volumen_kg': 'Session Volume (KG)', 
            'tipo_entrenamiento': 'Classification'
        }
    )
    
    fig.update_layout(
        template="simple_white",
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    
    # Clean trendline color
    fig.update_traces(selector=dict(mode="lines"), line=dict(color="#e74c3c", width=2, dash="dash"))
    
    st.plotly_chart(fig, use_container_width=True)

def render_data_lake_tab(df: pd.DataFrame):
    """Renders the raw tabular data for inspection."""
    st.markdown("#### Processed Data Warehouse")
    st.write("Tabular view of the refined dataset post-ETL pipeline execution.")
    
    st.dataframe(
        df.sort_values('fecha', ascending=False),
        use_container_width=True,
        hide_index=True
    )

def run_dashboard():
    """Main dashboard orchestration."""
    df_raw = load_data()
    
    if df_raw.empty:
        st.warning("Data repository is currently empty. Execute the backend ETL pipeline to populate.")
        st.stop()
        
    df_filtered = apply_sidebar_filters(df_raw)
    
    # Header
    st.title("Performance Analytics")
    st.write("Aggregated insights derived from automated ETL processing.")
    
    # Tabs layout
    tab1, tab2, tab3 = st.tabs(["Overview", "Biometric Correlations", "Data Repository"])
    
    with tab1:
        render_overview_tab(df_filtered)
        
    with tab2:
        render_correlations_tab(df_filtered)
        
    with tab3:
        render_data_lake_tab(df_filtered)

if __name__ == "__main__":
    run_dashboard()
