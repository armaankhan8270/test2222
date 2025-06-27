# src/finops_framework/insights/recommendations.py

import streamlit as st
import pandas as pd
from datetime import date
from typing import List, Dict, Any, Optional

# Import core components
from finops_framework.core.data_fetcher import DataFetcher, DataFetchError
from finops_framework.ui.base_components import display_error_box, display_warning_box
from finops_framework.utils import helpers # For any helper calculations

def generate_finops_recommendations(
    data_fetcher: DataFetcher,
    start_date: date,
    end_date: date,
    selected_user: Optional[str] = None,
    selected_warehouse: Optional[str] = None
) -> List[str]:
    """
    Analyzes FinOps data for the given period/entity and generates actionable recommendations.

    Args:
        data_fetcher (DataFetcher): An instance of DataFetcher.
        start_date (date): The start date of the analysis period.
        end_date (date): The end date of the analysis period.
        selected_user (Optional[str]): The user to analyze recommendations for (if applicable).
        selected_warehouse (Optional[str]): The warehouse to analyze recommendations for (if applicable).

    Returns:
        List[str]: A list of actionable FinOps recommendations.
    """
    recommendations: List[str] = []

    # --- Global/Overview Recommendations ---
    if not selected_user and not selected_warehouse:
        # Example 1: High overall idle time for warehouses
        try:
            warehouse_summary = data_fetcher.execute_query(
                "WAREHOUSE_SUMMARY_METRICS",
                params={"start_date": start_date, "end_date": end_date, "selected_warehouse_name": None} # Placeholder for all warehouses
            )
            if not warehouse_summary.empty:
                # We need a query that summarizes ALL warehouses, not just a selected one
                # Let's adjust query_store.py or assume a combined result.
                # For now, let's just use a simplified logic:
                # For a real scenario, you'd need a specific query for 'ALL_WAREHOUSE_IDLE_TIME'
                # Let's check for any warehouse with high idle time
                high_idle_warehouses = warehouse_summary[
                    (warehouse_summary['IDLE_PERCENTAGE'] > 20) & (warehouse_summary['TOTAL_CREDITS_USED'] > 0)
                ]
                for idx, row in high_idle_warehouses.iterrows():
                    recommendations.append(
                        f"Consider adjusting auto-suspend for warehouse **{row['WAREHOUSE_NAME']}** "
                        f"(Size: {row['SIZE']}) due to **{helpers.format_percentage(row['IDLE_PERCENTAGE']/100)}** idle time. "
                        "A shorter auto-suspend period can reduce costs."
                    )
        except DataFetchError as e:
            display_warning_box(f"Could not fetch warehouse data for recommendations: {e}")

        # Example 2: Overall cost trend (simple check)
        try:
            total_cost_data = data_fetcher.execute_query(
                "TOTAL_COST_AND_CREDITS_OVERVIEW",
                params={"start_date": start_date, "end_date": end_date,
                        "prev_start_date": data_fetcher.calculate_prev_period_dates(start_date, end_date)[0],
                        "prev_end_date": data_fetcher.calculate_prev_period_dates(start_date, end_date)[1]}
            )
            if not total_cost_data.empty:
                current_cost = total_cost_data['ESTIMATED_COST_USD'].iloc[0]
                prev_cost = total_cost_data['PREV_ESTIMATED_COST_USD'].iloc[0]
                delta_pct = helpers.calculate_delta_percentage(current_cost, prev_cost)

                if delta_pct is not None and delta_pct > 0.10: # If cost increased by more than 10%
                    recommendations.append(
                        f"Overall estimated cost increased by **{helpers.format_percentage(delta_pct)}** compared to the previous period. "
                        "Investigate top cost drivers (warehouses, users, services) for potential optimizations."
                    )
        except DataFetchError as e:
            display_warning_box(f"Could not fetch total cost data for recommendations: {e}")


    # --- User-Specific Recommendations ---
    if selected_user:
        try:
            user_summary_data = data_fetcher.execute_query(
                "USER_360_SUMMARY_METRICS",
                params={
                    "start_date": start_date, "end_date": end_date,
                    "prev_start_date": data_fetcher.calculate_prev_period_dates(start_date, end_date)[0],
                    "prev_end_date": data_fetcher.calculate_prev_period_dates(start_date, end_date)[1],
                    "selected_user_name": selected_user
                }
            )
            if not user_summary_data.empty:
                avg_query_duration_sec = user_summary_data['AVG_QUERY_DURATION_SEC'].iloc[0]
                avg_credits_per_query = user_summary_data['AVG_CREDITS_PER_QUERY'].iloc[0]
                failed_query_count = user_summary_data['FAILED_QUERY_COUNT'].iloc[0]
                total_query_count = user_summary_data['TOTAL_QUERY_COUNT'].iloc[0]

                if avg_query_duration_sec is not None and avg_query_duration_sec > 300: # Over 5 minutes
                    recommendations.append(
                        f"User **{selected_user}** has an average query duration of **{helpers.format_duration_seconds(avg_query_duration_sec)}**. "
                        "Review long-running queries for optimization (e.g., using better filters, indexing, or materialized views)."
                    )
                if avg_credits_per_query is not None and avg_credits_per_query > 1.0: # Arbitrary high credits per query
                    recommendations.append(
                        f"User **{selected_user}** shows high average credits per query (**{avg_credits_per_query:.2f}**). "
                        "Suggest reviewing query patterns for potential inefficiencies, especially large scans or joins."
                    )
                if total_query_count > 0 and (failed_query_count / total_query_count) > 0.05: # More than 5% failed queries
                    recommendations.append(
                        f"User **{selected_user}** has a **{helpers.format_percentage(failed_query_count / total_query_count)}** failed query rate. "
                        "Investigate common errors or complex queries failing frequently to improve user experience and reduce retries."
                    )
            
            # Check user's warehouse usage for idle time
            user_warehouse_util_data = data_fetcher.execute_query(
                "USER_WAREHOUSE_UTILIZATION_OVERVIEW",
                params={
                    "start_date": start_date, "end_date": end_date,
                    "selected_user_name": selected_user
                }
            )
            if not user_warehouse_util_data.empty:
                for idx, row in user_warehouse_util_data.iterrows():
                    if row['IDLE_PERCENTAGE_ON_WH_USER_USED'] is not None and row['IDLE_PERCENTAGE_ON_WH_USER_USED'] > 20:
                         recommendations.append(
                            f"User **{selected_user}** frequently uses warehouse **{row['WAREHOUSE_NAME']}** "
                            f"which has **{helpers.format_percentage(row['IDLE_PERCENTAGE_ON_WH_USER_USED']/100)}** idle time. "
                            "Ensure the user is selecting the most appropriate warehouse size and auto-suspend settings."
                        )

        except DataFetchError as e:
            display_warning_box(f"Could not fetch user data for recommendations: {e}")

    # --- Warehouse-Specific Recommendations ---
    if selected_warehouse:
        try:
            warehouse_summary_data = data_fetcher.execute_query(
                "WAREHOUSE_SUMMARY_METRICS",
                params={
                    "start_date": start_date, "end_date": end_date,
                    "prev_start_date": data_fetcher.calculate_prev_period_dates(start_date, end_date)[0],
                    "prev_end_date": data_fetcher.calculate_prev_period_dates(start_date, end_date)[1],
                    "selected_warehouse_name": selected_warehouse
                }
            )
            if not warehouse_summary_data.empty:
                idle_percentage = warehouse_summary_data['IDLE_PERCENTAGE'].iloc[0]
                auto_suspend_setting = warehouse_summary_data['AUTO_SUSPEND'].iloc[0]
                warehouse_size = warehouse_summary_data['SIZE'].iloc[0]
                total_active_minutes = warehouse_summary_data['ACTIVE_MINUTES'].iloc[0]

                if idle_percentage is not None and idle_percentage > 20 and auto_suspend_setting > 60 * 5: # More than 20% idle, auto-suspend > 5 min
                    recommendations.append(
                        f"Warehouse **{selected_warehouse}** has **{helpers.format_percentage(idle_percentage/100)}** idle time "
                        f"and an auto-suspend setting of **{helpers.format_duration_seconds(auto_suspend_setting)}**. "
                        "Consider reducing auto-suspend to 1 or 5 minutes to optimize cost."
                    )
                
                # Check for overloaded queues (indicates undersizing)
                queued_time_data = data_fetcher.execute_query(
                    "WAREHOUSE_QUEUED_OVERLOAD_TIME_TREND",
                    params={
                        "start_date": start_date, "end_date": end_date,
                        "selected_warehouse_name": selected_warehouse
                    }
                )
                if not queued_time_data.empty:
                    total_queued_time = queued_time_data['TOTAL_QUEUED_OVERLOAD_TIME_SEC'].sum()
                    if total_queued_time > 3600 * 0.5: # More than 30 minutes of total queued time
                        recommendations.append(
                            f"Warehouse **{selected_warehouse}** experienced **{helpers.format_duration_seconds(total_queued_time)}** "
                            "in queued overload time. This may indicate the warehouse is undersized for peak loads. "
                            "Consider temporarily or permanently increasing its size during high usage periods."
                        )
                
                # Check for potential over-sizing based on active minutes
                # This is a very rough heuristic
                if total_active_minutes < (end_date - start_date).days * 60 * 0.1 and warehouse_size not in ('X-SMALL', 'SMALL'): # If less than 10% active usage, and not smallest sizes
                    recommendations.append(
                        f"Warehouse **{selected_warehouse}** has relatively low active usage (**{total_active_minutes} minutes**) "
                        f"for its size (**{warehouse_size}**). If this pattern persists, consider rightsizing to a smaller warehouse."
                    )


        except DataFetchError as e:
            display_warning_box(f"Could not fetch warehouse data for recommendations: {e}")

    if not recommendations:
        return ["No specific recommendations at this time for the selected criteria. Keep monitoring!"]
    
    return recommendations

def display_recommendations_section(
    data_fetcher: DataFetcher,
    section_title: str,
    start_date: date,
    end_date: date,
    selected_user: Optional[str] = None,
    selected_warehouse: Optional[str] = None
):
    """
    Renders a section displaying FinOps recommendations.

    Args:
        data_fetcher (DataFetcher): An instance of DataFetcher.
        section_title (str): Title for this section.
        start_date (date): Start date for data analysis.
        end_date (date): End date for data analysis.
        selected_user (Optional[str]): The user for whom to generate recommendations.
        selected_warehouse (Optional[str]): The warehouse for which to generate recommendations.
    """
    display_section_header(section_title, description="Actionable insights to optimize your Snowflake costs.")

    recommendations = generate_finops_recommendations(
        data_fetcher, start_date, end_date, selected_user, selected_warehouse
    )

    if recommendations:
        for i, rec in enumerate(recommendations):
            st.markdown(f"- {rec}")
    else:
        st.info("No recommendations found for the selected period and criteria.")