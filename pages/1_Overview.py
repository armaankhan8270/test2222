# pages/1_Overview.py

import streamlit as st
from datetime import date

# Import core framework components
from finops_framework.core.data_fetcher import DataFetcher
from finops_framework.ui.base_components import date_range_selector, display_error_box
from finops_framework.modules.dashboard_sections import display_metric_section, display_chart_section
from finops_framework.insights.recommendations import display_recommendations_section

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.header("📊 Snowflake Cost Overview")

# Ensure data_fetcher is available in session_state, initialized in src/main.py
if "data_fetcher" not in st.session_state or not isinstance(st.session_state.data_fetcher, DataFetcher):
    display_error_box("Snowflake session not initialized. Please go back to the Home page (or rerun `src/main.py`) and ensure connection is established.")
    st.stop() # Stop execution if DataFetcher is not ready

data_fetcher: DataFetcher = st.session_state.data_fetcher

# --- Date Range Selector (in-page component) ---
st.markdown("---") # Visual separator
start_date, end_date = date_range_selector(data_fetcher, key_prefix="overview")
st.markdown("---") # Visual separator


# --- Display Metrics Section ---
st.subheader("Key Metrics")
display_metric_section(
    data_fetcher=data_fetcher,
    section_title="Account Summary",
    section_key="OVERVIEW_METRICS", # This key maps to configs in dashboard_configs.py
    start_date=start_date,
    end_date=end_date,
    num_columns=2 # Display metrics in 2 columns
)

# --- Display Charts Section ---
st.subheader("Cost Trends & Drivers")
display_chart_section(
    data_fetcher=data_fetcher,
    section_title="Overall Usage & Cost Trends",
    section_key="OVERVIEW_CHARTS", # This key maps to configs in dashboard_configs.py
    start_date=start_date,
    end_date=end_date,
    num_columns=2 # Display charts in 2 columns
)

# --- Display Recommendations Section ---
st.subheader("FinOps Recommendations")
display_recommendations_section(
    data_fetcher=data_fetcher,
    section_title="Account-Wide Optimizations",
    start_date=start_date,
    end_date=end_date
)