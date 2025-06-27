# src/finops_framework/modules/dashboard_sections.py

import streamlit as st
import pandas as pd
from typing import Tuple, Optional, Dict, Any
from datetime import date

# Import core framework components
from finops_framework.core.data_fetcher import DataFetcher, DataFetchError
from finops_framework.models.dashboard_configs import METRIC_CARD_CONFIGS, CHART_CONFIGS, APP_THEME
from finops_framework.ui.metric_card import render_metric_card
from finops_framework.ui.chart_renderer import render_chart
from finops_framework.ui.base_components import display_section_header, display_error_box, display_warning_box
from finops_framework.utils import helpers # For delta calculations and custom formatters

def display_metric_section(
    data_fetcher: DataFetcher,
    section_title: str,
    section_key: str, # Key to access configs (e.g., "OVERVIEW_METRICS", "USER_360_METRICS")
    start_date: date,
    end_date: date,
    selected_entity: Optional[str] = None, # For user/warehouse specific queries
    num_columns: int = 3 # How many metric cards per row
):
    """
    Renders a section of metric cards based on predefined configurations.

    Args:
        data_fetcher (DataFetcher): Instance of DataFetcher.
        section_title (str): Title for this section (displayed using display_section_header).
        section_key (str): Key to retrieve metric configurations from METRIC_CARD_CONFIGS.
        start_date (date): Start date for data queries.
        end_date (date): End date for data queries.
        selected_entity (Optional[str]): The selected user/warehouse name, if applicable.
        num_columns (int): Number of columns to use for displaying metric cards.
    """
    display_section_header(section_title)

    metric_configs = METRIC_CARD_CONFIGS.get(section_key, [])
    if not metric_configs:
        display_warning_box(f"No metric configurations found for section key: '{section_key}'.")
        return

    # Calculate previous period dates once for all metrics
    prev_start_date, prev_end_date = data_fetcher.calculate_prev_period_dates(start_date, end_date)

    cols = st.columns(num_columns)
    col_idx = 0

    for config in metric_configs:
        with cols[col_idx]:
            label = config.get("label", "Unknown Metric")
            query_id = config.get("query_id")
            value_col = config.get("value_col")
            delta_col = config.get("delta_col")
            format_value = config.get("format_value", "{:,.0f}")
            format_delta = config.get("format_delta", "{:+.2%}")
            formatter_func = config.get("formatter_func")
            help_text = config.get("help_text")

            if not query_id or not value_col:
                display_error_box(f"Incomplete config for metric '{label}': missing query_id or value_col.")
                continue

            params = {
                "start_date": start_date,
                "end_date": end_date,
                "prev_start_date": prev_start_date,
                "prev_end_date": prev_end_date
            }
            if selected_entity:
                if section_key.startswith("USER_"):
                    params["selected_user_name"] = selected_entity
                elif section_key.startswith("WAREHOUSE_"):
                    params["selected_warehouse_name"] = selected_entity

            try:
                data = data_fetcher.execute_query(query_id, params)

                current_value = None
                previous_value = None

                if not data.empty and value_col in data.columns:
                    current_value = data[value_col].iloc[0]
                    if delta_col and delta_col in data.columns:
                        previous_value = data[delta_col].iloc[0]
                
                # --- Special Handling for Calculated Metrics (e.g., Failed Query Rate) ---
                if label == "Failed Query Rate" and section_key == "USER_360_METRICS":
                    total_queries = data['TOTAL_QUERY_COUNT'].iloc[0] if 'TOTAL_QUERY_COUNT' in data.columns and not data.empty else 0
                    failed_queries = data['FAILED_QUERY_COUNT'].iloc[0] if 'FAILED_QUERY_COUNT' in data.columns and not data.empty else 0
                    
                    if total_queries > 0:
                        current_value = failed_queries / total_queries
                    else:
                        current_value = 0.0 # No queries, so 0% failed rate
                    # Delta for failed query rate is usually not calculated this way; it's a direct rate.
                    previous_value = None # Ensure delta is not shown for this metric if not applicable

                render_metric_card(
                    label=label,
                    value=current_value,
                    delta=previous_value,
                    format_value=format_value,
                    format_delta=format_delta,
                    formatter_func=formatter_func,
                    help_text=help_text,
                    theme_config=APP_THEME
                )

            except DataFetchError as e:
                display_error_box(f"Failed to load metric '{label}': {e}")
            except KeyError:
                display_error_box(f"Data for metric '{label}' is missing expected columns. Check query_store.py or dashboard_configs.py.")
            except Exception as e:
                display_error_box(f"An unexpected error occurred for metric '{label}': {e}")

        col_idx = (col_idx + 1) % num_columns

def display_chart_section(
    data_fetcher: DataFetcher,
    section_title: str,
    section_key: str, # Key to access configs (e.g., "OVERVIEW_CHARTS", "USER_360_CHARTS")
    start_date: date,
    end_date: date,
    selected_entity: Optional[str] = None, # For user/warehouse specific queries
    num_columns: int = 2 # How many charts per row
):
    """
    Renders a section of charts based on predefined configurations.

    Args:
        data_fetcher (DataFetcher): Instance of DataFetcher.
        section_title (str): Title for this section (displayed using display_section_header).
        section_key (str): Key to retrieve chart configurations from CHART_CONFIGS.
        start_date (date): Start date for data queries.
        end_date (date): End date for data queries.
        selected_entity (Optional[str]): The selected user/warehouse name, if applicable.
        num_columns (int): Number of columns to use for displaying charts.
    """
    display_section_header(section_title)

    chart_configs = CHART_CONFIGS.get(section_key, [])
    if not chart_configs:
        display_warning_box(f"No chart configurations found for section key: '{section_key}'.")
        return

    cols = st.columns(num_columns)
    col_idx = 0

    for config in chart_configs:
        with cols[col_idx]:
            title = config.get("title", "Unknown Chart")
            query_id = config.get("query_id")

            if not query_id:
                display_error_box(f"Incomplete config for chart '{title}': missing query_id.")
                continue

            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            if selected_entity:
                if section_key.startswith("USER_"):
                    params["selected_user_name"] = selected_entity
                elif section_key.startswith("WAREHOUSE_"):
                    params["selected_warehouse_name"] = selected_entity

            try:
                data = data_fetcher.execute_query(query_id, params)
                render_chart(data, config, APP_THEME)

            except DataFetchError as e:
                display_error_box(f"Failed to load chart '{title}': {e}")
            except KeyError:
                display_error_box(f"Data for chart '{title}' is missing expected columns. Check query_store.py or dashboard_configs.py.")
            except Exception as e:
                display_error_box(f"An unexpected error occurred for chart '{title}': {e}")

        col_idx = (col_idx + 1) % num_columns