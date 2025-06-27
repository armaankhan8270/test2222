# src/finops_framework/ui/base_components.py

import streamlit as st
from datetime import date, timedelta
from typing import Tuple, Optional, List, Union
import pandas as pd

# Import our configurations and core data fetcher
from finops_framework.models.dashboard_configs import DATE_RANGE_OPTIONS, APP_THEME
from finops_framework.core.data_fetcher import DataFetcher, DataFetchError

def date_range_selector(
    data_fetcher: DataFetcher, # Pass data_fetcher to get default start date from data
    key_prefix: str = "",
    default_days: int = 30 # Default to last 30 days
) -> Tuple[date, date]:
    """
    Renders a date range selector allowing pre-defined ranges or custom selection.
    Placed within the main content area.

    Args:
        data_fetcher (DataFetcher): An instance of DataFetcher to query min/max dates if needed.
        key_prefix (str): A unique prefix for Streamlit widget keys to avoid conflicts.
        default_days (int): The number of days for the default "Last X Days" selection.

    Returns:
        Tuple[date, date]: A tuple containing (start_date, end_date).
    """
    st.markdown(f"**Select Date Range**")
    
    # Get the latest date from query history if possible, otherwise use today
    try:
        # We need a small query to get max date from query history if possible
        # Or, just assume current date for simplicity in UI component.
        # For now, let's assume `date.today()` is sufficient for default_end_date
        # A more robust solution might query SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        # for MAX(START_TIME) as the most recent data point.
        # For simplicity of this component, let's assume `date.today()`.
        pass
    except DataFetchError:
        st.warning("Could not fetch latest data date. Using current date for range calculation.")
    
    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=default_days - 1) # -1 to include today

    selected_option = st.selectbox(
        "Choose a preset or custom range:",
        options=list(DATE_RANGE_OPTIONS.keys()),
        index=list(DATE_RANGE_OPTIONS.keys()).index(f"Last {default_days} Days") if f"Last {default_days} Days" in DATE_RANGE_OPTIONS else 0,
        key=f"{key_prefix}_date_range_preset_select"
    )

    if DATE_RANGE_OPTIONS[selected_option] is not None:
        # Predefined range
        days = DATE_RANGE_OPTIONS[selected_option]
        end_date = default_end_date # Always end today for presets
        start_date = end_date - timedelta(days=days - 1)
        st.info(f"Showing data from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**")
    else:
        # Custom range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date:",
                value=default_start_date,
                key=f"{key_prefix}_custom_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date:",
                value=default_end_date,
                key=f"{key_prefix}_custom_end_date"
            )
        
        if start_date > end_date:
            st.error("Error: End date must be after start date.")
            # Fallback to default if invalid selection
            start_date = default_start_date
            end_date = default_end_date

        st.info(f"Showing data from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**")

    return start_date, end_date


def entity_selector(
    data_fetcher: DataFetcher,
    entity_type: str, # "user" or "warehouse"
    key_prefix: str = ""
) -> Optional[str]:
    """
    Renders a dropdown selector for users or warehouses.

    Args:
        data_fetcher (DataFetcher): An instance of DataFetcher to query active entities.
        entity_type (str): The type of entity to select ("user" or "warehouse").
        key_prefix (str): A unique prefix for Streamlit widget keys.

    Returns:
        Optional[str]: The selected entity name, or None if no entities are found.
    """
    st.markdown(f"**Select {entity_type.capitalize()}**")

    query_id = f"LIST_ACTIVE_{entity_type.upper()}S_BY_COST" # e.g., LIST_ACTIVE_USERS_BY_COST

    try:
        # Fetch active entities (users or warehouses) based on cost in last 90 days
        # This is a fixed period for listing active entities, not tied to dashboard date range
        entity_data = data_fetcher.execute_query(query_id)
        
        if entity_data.empty:
            st.warning(f"No active {entity_type}s found in the last 90 days.")
            return None

        # Extract entity names, sort them alphabetically for consistent display
        entity_names = sorted(entity_data[f"{entity_type.upper()}_NAME"].unique().tolist())
        
        selected_entity = st.selectbox(
            f"Choose a {entity_type}:",
            options=entity_names,
            key=f"{key_prefix}_{entity_type}_select"
        )
        return selected_entity

    except DataFetchError as e:
        st.error(f"Failed to load {entity_type}s: {e}")
        return None
    except KeyError:
        st.error(f"Data for {entity_type}s is missing expected columns. Check query_store.py.")
        return None

def display_section_header(title: str, description: Optional[str] = None):
    """
    Renders a consistent, styled section header.
    """
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"<p style='color:{APP_THEME['text_color']}; opacity:0.8;'>{description}</p>", unsafe_allow_html=True)
    st.markdown("---") # Visual separator

def display_info_box(message: str, icon: str = "ℹ️"):
    """
    Displays an informative message box.
    """
    st.info(f"{icon} {message}")

def display_warning_box(message: str, icon: str = "⚠️"):
    """
    Displays a warning message box.
    """
    st.warning(f"{icon} {message}")

def display_error_box(message: str, icon: str = "❌"):
    """
    Displays an error message box.
    """
    st.error(f"{icon} {message}")