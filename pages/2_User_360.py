# pages/2_User_360.py

import streamlit as st
from datetime import date

# Import core framework components
from finops_framework.core.data_fetcher import DataFetcher
from finops_framework.ui.base_components import date_range_selector, entity_selector, display_error_box, display_warning_box
from finops_framework.modules.dashboard_sections import display_metric_section, display_chart_section
from finops_framework.insights.recommendations import display_recommendations_section

st.set_page_config(page_title="User 360", page_icon="👤", layout="wide")

st.header("👤 User 360: Detailed User FinOps Insights")

# Ensure data_fetcher is available in session_state, initialized in src/main.py
if "data_fetcher" not in st.session_state or not isinstance(st.session_state.data_fetcher, DataFetcher):
    display_error_box("Snowflake session not initialized. Please go back to the Home page (or rerun `src/main.py`) and ensure connection is established.")
    st.stop()

data_fetcher: DataFetcher = st.session_state.data_fetcher

# --- Date Range Selector (in-page component) ---
st.markdown("---") # Visual separator
start_date, end_date = date_range_selector(data_fetcher, key_prefix="user_360_date")
st.markdown("---") # Visual separator

# --- User Selector (in-page component) ---
selected_user = entity_selector(data_fetcher, entity_type="user", key_prefix="user_360_selector")

if selected_user:
    st.success(f"Displaying data for user: **{selected_user}**")
    st.markdown("---")

    # --- Display User-Specific Metrics Section ---
    st.subheader(f"Metrics for {selected_user}")
    display_metric_section(
        data_fetcher=data_fetcher,
        section_title=f"{selected_user}'s Performance Summary",
        section_key="USER_360_METRICS", # This key maps to configs in dashboard_configs.py
        start_date=start_date,
        end_date=end_date,
        selected_entity=selected_user, # Pass the selected user to filter data
        num_columns=3 # Display metrics in 3 columns
    )

    # --- Display User-Specific Charts Section ---
    st.subheader(f"Usage & Cost Patterns for {selected_user}")
    display_chart_section(
        data_fetcher=data_fetcher,
        section_title=f"{selected_user}'s Detailed Insights",
        section_key="USER_360_CHARTS", # This key maps to configs in dashboard_configs.py
        start_date=start_date,
        end_date=end_date,
        selected_entity=selected_user, # Pass the selected user to filter data
        num_columns=2 # Display charts in 2 columns
    )

    # --- Display Recommendations Section for the Selected User ---
    st.subheader(f"Recommendations for {selected_user}")
    display_recommendations_section(
        data_fetcher=data_fetcher,
        section_title=f"Optimization Insights for {selected_user}",
        start_date=start_date,
        end_date=end_date,
        selected_user=selected_user # Pass the selected user for user-specific recommendations
    )

else:
    # Message displayed if no user is selected or found
    display_warning_box("Please select a user from the dropdown above to view their FinOps insights.")