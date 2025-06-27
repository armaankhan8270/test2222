# src/finops_framework/models/dashboard_configs.py

from typing import Dict, Any, List, Optional

# --- 1. Global Theme Configuration ---
# Using a light theme as requested.
APP_THEME = {
    "primary_color": "#007BFF",  # Blue
    "background_color": "#F0F2F6", # Light gray/off-white
    "secondary_background_color": "#FFFFFF", # White
    "text_color": "#212529",     # Dark gray/black
    "font": "Segoe UI",         # Common, clean font
    "chart_height": 350,         # Default chart height
    "chart_colors": [            # A palette of accessible colors for charts
        "#007BFF", "#28A745", "#FFC107", "#DC3545", "#6F42C1",
        "#17A2B8", "#FD7E14", "#E83E8C", "#6C757D", "#20C997"
    ]
}

# --- 2. Date Range Presets ---
DATE_RANGE_OPTIONS = {
    "Last 7 Days": 7,
    "Last 30 Days": 30,
    "Last 90 Days": 90,
    "Last 1 Year": 365,
    "Custom Range": None # Sentinel value for custom date picker
}

# --- 3. Metric Card Definitions ---
# Each dictionary defines a metric card.
# 'value_col' and 'delta_col' correspond to column names in the DataFrame fetched by 'query_id'.
# 'format_value' and 'format_delta' are f-string compatible formats.
# 'formatter_func' allows custom Python functions for complex formatting (e.g., bytes to GB).
METRIC_CARD_CONFIGS: Dict[str, List[Dict[str, Any]]] = {
    "OVERVIEW_METRICS": [
        {
            "label": "Total Credits Used",
            "query_id": "TOTAL_COST_AND_CREDITS_OVERVIEW",
            "value_col": "TOTAL_CREDITS",
            "delta_col": "PREV_TOTAL_CREDITS",
            "format_value": "{:,.0f}",
            "format_delta": "{:+.2%}",
            "help_text": "Total Snowflake credits consumed in the selected period."
        },
        {
            "label": "Estimated Total Cost",
            "query_id": "TOTAL_COST_AND_CREDITS_OVERVIEW",
            "value_col": "ESTIMATED_COST_USD",
            "delta_col": "PREV_ESTIMATED_COST_USD",
            "format_value": "${:,.2f}",
            "format_delta": "{:+.2%}",
            "help_text": "Estimated cost based on consumed credits (assuming $2/credit)."
        }
    ],
    "USER_360_METRICS": [
        {
            "label": "Total Credits (User)",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "TOTAL_CREDITS",
            "delta_col": "PREV_TOTAL_CREDITS",
            "format_value": "{:,.0f}",
            "format_delta": "{:+.2%}",
            "help_text": "Total Snowflake credits consumed by this user in the selected period."
        },
        {
            "label": "Estimated Cost (User)",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "ESTIMATED_COST_USD",
            "delta_col": "PREV_ESTIMATED_COST_USD",
            "format_value": "${:,.2f}",
            "format_delta": "{:+.2%}",
            "help_text": "Estimated cost for this user (assuming $2/credit)."
        },
        {
            "label": "Avg. Query Duration",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "AVG_QUERY_DURATION_SEC",
            "delta_col": None,
            "format_value": "{:,.1f}s", # Default formatter
            "formatter_func": "format_duration_seconds", # Custom helper function
            "help_text": "Average execution time of queries run by this user."
        },
        {
            "label": "Avg. Credits/Query",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "AVG_CREDITS_PER_QUERY",
            "delta_col": None,
            "format_value": "{:,.3f}",
            "help_text": "Average credits consumed per query by this user. High value might indicate inefficient queries."
        },
        {
            "label": "Total Query Count",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "TOTAL_QUERY_COUNT",
            "delta_col": None,
            "format_value": "{:,.0f}",
            "help_text": "Total number of queries executed by this user."
        },
        {
            "label": "Failed Query Rate",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "FAILED_QUERY_RATE", # This will be calculated in Python, not directly from query
            "delta_col": None,
            "format_value": "{:.1%}",
            "formatter_func": "format_percentage", # Custom helper function
            "help_text": "Percentage of queries that failed for this user. High rate indicates issues."
        },
        {
            "label": "Total Data Scanned",
            "query_id": "USER_360_SUMMARY_METRICS",
            "value_col": "TOTAL_BYTES_SCANNED",
            "delta_col": None,
            "format_value": "{:,.2f} GB", # Default formatter
            "formatter_func": "format_bytes", # Custom helper function
            "help_text": "Total data scanned by user's queries. High volume can lead to high cost."
        }
    ],
    "WAREHOUSE_METRICS": [
        {
            "label": "Total Credits (Warehouse)",
            "query_id": "WAREHOUSE_SUMMARY_METRICS",
            "value_col": "TOTAL_CREDITS_USED",
            "delta_col": "PREV_TOTAL_CREDITS_USED",
            "format_value": "{:,.0f}",
            "format_delta": "{:+.2%}",
            "help_text": "Total Snowflake credits consumed by this warehouse in the selected period."
        },
        {
            "label": "Estimated Cost (Warehouse)",
            "query_id": "WAREHOUSE_SUMMARY_METRICS",
            "value_col": "ESTIMATED_COST_USD",
            "delta_col": "PREV_ESTIMATED_COST_USD",
            "format_value": "${:,.2f}",
            "format_delta": "{:+.2%}",
            "help_text": "Estimated cost for this warehouse (assuming $2/credit)."
        },
        {
            "label": "Idle Percentage",
            "query_id": "WAREHOUSE_SUMMARY_METRICS",
            "value_col": "IDLE_PERCENTAGE",
            "delta_col": None,
            "format_value": "{:.1%}",
            "formatter_func": "format_percentage",
            "help_text": "Percentage of time the warehouse was running but idle. High value indicates over-provisioning or poor auto-suspend settings."
        },
        {
            "label": "Total Active Minutes",
            "query_id": "WAREHOUSE_SUMMARY_METRICS",
            "value_col": "ACTIVE_MINUTES",
            "delta_col": None,
            "format_value": "{:,.0f} min",
            "help_text": "Total minutes the warehouse was actively processing queries."
        },
        {
            "label": "Auto Suspend",
            "query_id": "WAREHOUSE_SUMMARY_METRICS",
            "value_col": "AUTO_SUSPEND",
            "delta_col": None,
            "format_value": "{:,.0f} s",
            "help_text": "Current AUTO_SUSPEND setting for the warehouse."
        }
    ]
}

# --- 4. Chart Definitions ---
# Each dictionary defines a chart.
# 'chart_type' maps to functions in chart_renderer.py.
# 'x_col', 'y_col', 'color_col' map to DataFrame columns.
# 'sort_desc' is a common option for bar charts.
CHART_CONFIGS: Dict[str, List[Dict[str, Any]]] = {
    "OVERVIEW_CHARTS": [
        {
            "title": "Daily Credit Consumption Trend",
            "description": "Total daily credit consumption across all services.",
            "query_id": "DAILY_CREDIT_CONSUMPTION_TREND",
            "chart_type": "line",
            "x_col": "USAGE_DAY",
            "y_col": "DAILY_CREDITS_USED",
            "x_axis_title": "Date",
            "y_axis_title": "Credits Used"
        },
        {
            "title": "Estimated Cost by Service Type",
            "description": "Cost breakdown by Snowflake service type (e.g., Compute, Storage, Cloud Services).",
            "query_id": "COST_BY_SERVICE_TYPE",
            "chart_type": "bar",
            "x_col": "SERVICE_TYPE",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Service Type",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "Top 10 Warehouses by Cost",
            "description": "The warehouses incurring the highest costs.",
            "query_id": "TOP_10_WAREHOUSES_BY_COST",
            "chart_type": "bar",
            "x_col": "WAREHOUSE_NAME",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Warehouse Name",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "Top 10 Users by Cost",
            "description": "The users incurring the highest costs.",
            "query_id": "TOP_10_USERS_BY_COST",
            "chart_type": "bar",
            "x_col": "USER_NAME",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "User Name",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        }
    ],
    "USER_360_CHARTS": [
        {
            "title": "User's Daily Credit Consumption Trend",
            "description": "Visualizes daily credit consumption by the selected user to identify personal trends.",
            "query_id": "USER_DAILY_CREDIT_CONSUMPTION",
            "chart_type": "line",
            "x_col": "USAGE_DAY",
            "y_col": "DAILY_CREDITS_USED",
            "x_axis_title": "Date",
            "y_axis_title": "Credits Used"
        },
        {
            "title": "User's Estimated Cost by Query Type",
            "description": "Breakdown of estimated costs by the types of queries run by this user (e.g., SELECT, DML, DDL).",
            "query_id": "USER_QUERY_TYPE_DISTRIBUTION",
            "chart_type": "bar",
            "x_col": "QUERY_TYPE",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Query Type",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "User's Top 10 Warehouses by Estimated Cost",
            "description": "Warehouses where the user incurred the highest estimated costs. Consider if the right warehouse size/type is being used.",
            "query_id": "USER_WAREHOUSE_COST_BREAKDOWN",
            "chart_type": "bar",
            "x_col": "WAREHOUSE_NAME",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Warehouse Name",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "User's Top 10 Roles by Estimated Cost",
            "description": "Snowflake roles the user frequently assumed that incurred the highest estimated costs. Review role privileges and usage patterns.",
            "query_id": "USER_ROLE_COST_BREAKDOWN",
            "chart_type": "bar",
            "x_col": "ROLE_NAME",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Role Name",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "Underutilized Warehouses (Used by User)",
            "description": "Warehouses used by this user that exhibit significant idle time. Opportunities to adjust AUTO_SUSPEND.",
            "query_id": "USER_WAREHOUSE_UTILIZATION_OVERVIEW",
            "chart_type": "table" # Display as table for detailed review
        },
        {
            "title": "User's Top 20 Most Expensive Queries",
            "description": "The user's queries that consumed the most credits. Prioritize these for optimization, examining `QUERY_TEXT`.",
            "query_id": "USER_TOP_EXPENSIVE_QUERIES",
            "chart_type": "table"
        },
        {
            "title": "User's Top 20 Longest Running Queries",
            "description": "The user's queries with the longest execution times. Analyze `QUEUED_OVERLOAD_TIME` and `COMPILATION_TIME` for bottlenecks.",
            "query_id": "USER_TOP_LONG_RUNNING_QUERIES",
            "chart_type": "table"
        }
    ],
    "WAREHOUSE_INSIGHTS_CHARTS": [
        {
            "title": "Warehouse Daily Credit Consumption",
            "description": "Trend of daily credit consumption for the selected warehouse.",
            "query_id": "WAREHOUSE_DAILY_CREDIT_CONSUMPTION",
            "chart_type": "line",
            "x_col": "USAGE_DAY",
            "y_col": "DAILY_CREDITS_USED",
            "x_axis_title": "Date",
            "y_axis_title": "Credits Used"
        },
        {
            "title": "Warehouse Query Completion Status",
            "description": "Breakdown of query success vs. failure rates for this warehouse.",
            "query_id": "WAREHOUSE_QUERY_COMPLETION_STATUS",
            "chart_type": "pie", # New chart type!
            "name_col": "STATUS",
            "value_col": "QUERY_COUNT",
            "x_axis_title": "Status", # Not directly used by pie, but good for context
            "y_axis_title": "Query Count" # Not directly used by pie, but good for context
        },
        {
            "title": "Warehouse Query Completion Cost",
            "description": "Cost breakdown by query success vs. failure rates for this warehouse.",
            "query_id": "WAREHOUSE_QUERY_COMPLETION_STATUS",
            "chart_type": "pie", # New chart type!
            "name_col": "STATUS",
            "value_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Status",
            "y_axis_title": "Estimated Cost (USD)"
        },
        {
            "title": "Top 10 Users on this Warehouse by Cost",
            "description": "Users who incurred the most cost on this specific warehouse.",
            "query_id": "WAREHOUSE_TOP_USERS_BY_COST",
            "chart_type": "bar",
            "x_col": "USER_NAME",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "User Name",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "Top 10 Roles on this Warehouse by Cost",
            "description": "Roles that incurred the most cost on this specific warehouse.",
            "query_id": "WAREHOUSE_TOP_ROLES_BY_COST",
            "chart_type": "bar",
            "x_col": "ROLE_NAME",
            "y_col": "ESTIMATED_COST_USD",
            "x_axis_title": "Role Name",
            "y_axis_title": "Estimated Cost (USD)",
            "sort_desc": True
        },
        {
            "title": "Warehouse Queued Overload Time Trend",
            "description": "Daily trend of time queries spent queued due to warehouse overload. High values indicate undersized warehouse.",
            "query_id": "WAREHOUSE_QUEUED_OVERLOAD_TIME_TREND",
            "chart_type": "line",
            "x_col": "USAGE_DAY",
            "y_col": "TOTAL_QUEUED_OVERLOAD_TIME_SEC",
            "x_axis_title": "Date",
            "y_axis_title": "Total Queued Time (seconds)"
        }
    ]
}