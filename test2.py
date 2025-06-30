# user_360_dashboard.py
import streamlit as st
from snowflake.snowpark.context import get_active_session
from query_store import QueryStore
from chart_renderer import ChartRenderer
from metric_renderer import MetricCardRenderer
import datetime as dt

# Initialize session and components
session = get_active_session()
query_store = QueryStore(session)
chart_renderer = ChartRenderer(query_store)
metric_renderer = MetricCardRenderer(query_store)

# Page configuration
st.set_page_config(
    page_title="Snowflake User 360°",
    layout="wide",
    page_icon="👤"
)
st.title("❄️ Snowflake User 360° Dashboard")
st.markdown("### User-level Cost & Performance Analytics")

# Filters sidebar
with st.sidebar:
    st.header("🔍 Filters")
    date_range = st.selectbox(
        "Date Range", 
        ["7d", "30d", "3m", "6m", "1y", "ytd"], 
        index=1,
        help="Analyze costs over different time periods"
    )
    
    user_options = query_store.run_query("active_users", date_range)["USER_NAME"].tolist()
    selected_user = st.selectbox(
        "Select User",
        options=user_options,
        index=0,
        help="Focus analysis on specific users"
    )
    
    st.divider()
    st.markdown("**Cost Optimization Tips**")
    st.info("""
    - 🚀 Reduce long-running queries
    - 📉 Downsize underutilized warehouses
    - 🕒 Schedule off-hours maintenance
    - 🔍 Monitor storage growth trends
    """)

# Cost Summary Metrics
st.subheader("💰 Cost Summary")
cost_cols = st.columns(4)
with cost_cols[0]:
    metric_renderer.render(
        "user_spend", 
        "Total Spend", 
        "spend", 
        date_range, 
        selected_user, 
        prefix="$", 
        precision=0
    )
with cost_cols[1]:
    metric_renderer.render(
        "avg_cost_per_query", 
        "Avg Cost/Query", 
        "cost", 
        date_range, 
        selected_user, 
        prefix="$", 
        precision=4
    )
with cost_cols[2]:
    metric_renderer.render(
        "storage_cost", 
        "Storage Cost", 
        "storage", 
        date_range, 
        prefix="$", 
        precision=2
    )
with cost_cols[3]:
    metric_renderer.render(
        "cost_efficiency", 
        "Cost Efficiency", 
        "efficiency", 
        date_range, 
        selected_user, 
        suffix="%",
        help="(Queries per $ spent)"
    )

# Performance Metrics
st.subheader("⚡ Performance Metrics")
perf_cols = st.columns(4)
with perf_cols[0]:
    metric_renderer.render(
        "avg_query_time", 
        "Avg Query Time", 
        "time", 
        date_range, 
        selected_user, 
        suffix="ms"
    )
with perf_cols[1]:
    metric_renderer.render(
        "total_queries", 
        "Total Queries", 
        "queries", 
        date_range, 
        selected_user
    )
with perf_cols[2]:
    metric_renderer.render(
        "failed_queries", 
        "Failed Queries", 
        "error", 
        date_range, 
        selected_user
    )
with perf_cols[3]:
    metric_renderer.render(
        "warehouse_efficiency", 
        "Warehouse Efficiency", 
        "warehouse", 
        date_range, 
        selected_user, 
        suffix="%",
        help="(Credit utilization vs allocated)"
    )

# Optimization Recommendations
st.subheader("🎯 Optimization Opportunities")
with st.expander("View Cost-Saving Recommendations", expanded=True):
    rec_cols = st.columns(3)
    
    with rec_cols[0]:
        st.metric(label="Potential Savings", value="$4,200/mo", 
                 delta="-18% possible", delta_color="inverse")
        st.progress(65)
        st.caption("Reduce oversized warehouse usage")
        
    with rec_cols[1]:
        st.metric(label="Long Queries", value="27", 
                 delta="+8% from last month", delta_color="inverse")
        st.progress(40)
        st.caption("Optimize complex queries")
        
    with rec_cols[2]:
        st.metric(label="Idle Warehouses", value="3", 
                 delta="2 active overnight")
        st.progress(20)
        st.caption("Schedule auto-suspension")

# Charts Section
st.subheader("📊 Cost & Performance Analysis")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Cost Breakdown
    chart_renderer.render(
        "cost_by_warehouse", 
        "bar", 
        "Cost by Warehouse", 
        date_range, 
        selected_user,
        x="WAREHOUSE_NAME", 
        y="TOTAL_COST",
        text_auto="$.2f",
        height=400
    )
    
    # Query Performance
    chart_renderer.render(
        "query_performance", 
        "scatter", 
        "Query Performance Analysis", 
        date_range, 
        selected_user,
        x="EXECUTION_TIME", 
        y="CREDITS_USED",
        color="QUERY_TYPE",
        size="DATA_SCANNED_GB",
        hover_name="QUERY_TEXT",
        log_x=True,
        height=500
    )
    
    # Storage Trends
    chart_renderer.render(
        "storage_growth", 
        "area", 
        "Storage Growth Trend", 
        date_range,
        x="USAGE_DATE", 
        y="STORAGE_COST",
        height=350
    )

with chart_col2:
    # Cost Over Time
    chart_renderer.render(
        "cost_over_time", 
        "line", 
        "Daily Spend Trend", 
        date_range, 
        selected_user,
        x="DATE", 
        y="DAILY_COST",
        height=400
    )
    
    # Warehouse Utilization
    chart_renderer.render(
        "warehouse_utilization", 
        "treemap", 
        "Warehouse Utilization", 
        date_range, 
        selected_user,
        path=["WAREHOUSE_NAME", "QUERY_TYPE"], 
        values="CREDITS_USED",
        height=500
    )
    
    # Top Costly Queries
    chart_renderer.render(
        "costly_queries", 
        "bar", 
        "Top 10 Costly Queries", 
        date_range, 
        selected_user,
        x="QUERY_COST", 
        y="QUERY_ID",
        orientation="h",
        text_auto="$.2f",
        height=350
    )

# Full-width chart
chart_renderer.render(
    "long_running_queries", 
    "table", 
    "Long-Running Queries (Optimization Targets)", 
    date_range, 
    selected_user,
    columns=["QUERY_TEXT", "USER_NAME", "EXECUTION_MIN", "CREDITS_USED"],
    height=400
)

# Footer
st.divider()
st.caption("""
**Cost Optimization Strategy**: 
Monitor daily spend trends, identify inefficient warehouses, optimize long-running queries, 
and review storage growth monthly. Schedule resource-intensive jobs during off-peak hours.
""")






# Add to QueryStore._load_query_templates()
class QueryStore:
    def _load_query_templates(self) -> Dict[str, str]:
        return {
            # ... existing queries ...
            
            # New optimized queries for User 360
            "active_users": """
                SELECT DISTINCT USER_NAME
                FROM QUERY_HISTORY
                WHERE START_TIME > DATEADD(month, -3, CURRENT_DATE())
                ORDER BY USER_NAME
            """,
            
            "user_spend": """
                SELECT SUM(CREDITS_USED * CREDIT_PRICE) AS TOTAL_SPEND 
                FROM METERING_HISTORY 
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
            """,
            
            "avg_cost_per_query": """
                SELECT 
                    SUM(CREDITS_USED * CREDIT_PRICE) / COUNT(*) AS AVG_COST_PER_QUERY
                FROM METERING_HISTORY 
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
            """,
            
            "cost_efficiency": """
                SELECT
                    (COUNT(*) / NULLIF(SUM(CREDITS_USED * CREDIT_PRICE), 0)) * 10000 AS EFFICIENCY_SCORE
                FROM METERING_HISTORY
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
            """,
            
            "failed_queries": """
                SELECT COUNT(*) AS FAILED_COUNT
                FROM QUERY_HISTORY
                WHERE ERROR_CODE IS NOT NULL
                AND USER_NAME = '{user_id}'
                {{date_filter}}
            """,
            
            "warehouse_efficiency": """
                SELECT
                    AVG(CREDITS_USED / NULLIF(CREDITS_ALLOCATED, 0)) * 100 AS UTILIZATION_PCT
                FROM WAREHOUSE_METERING_HISTORY
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
            """,
            
            "cost_by_warehouse": """
                SELECT 
                    WAREHOUSE_NAME,
                    SUM(CREDITS_USED * CREDIT_PRICE) AS TOTAL_COST
                FROM METERING_HISTORY
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
                GROUP BY WAREHOUSE_NAME
                ORDER BY TOTAL_COST DESC
                LIMIT 10
            """,
            
            "query_performance": """
                SELECT
                    QUERY_ID,
                    QUERY_TEXT,
                    QUERY_TYPE,
                    EXECUTION_TIME / 1000 AS EXECUTION_TIME,
                    CREDITS_USED,
                    BYTES_SCANNED / POW(1024, 3) AS DATA_SCANNED_GB
                FROM QUERY_HISTORY
                WHERE USER_NAME = '{user_id}'
                AND EXECUTION_TIME > 0
                {{date_filter}}
                ORDER BY CREDITS_USED DESC
                LIMIT 100
            """,
            
            "cost_over_time": """
                SELECT
                    DATE(START_TIME) AS DATE,
                    SUM(CREDITS_USED * CREDIT_PRICE) AS DAILY_COST
                FROM METERING_HISTORY
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
                GROUP BY DATE
                ORDER BY DATE
            """,
            
            "warehouse_utilization": """
                SELECT
                    WAREHOUSE_NAME,
                    QUERY_TYPE,
                    SUM(CREDITS_USED) AS CREDITS_USED
                FROM METERING_HISTORY
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
                GROUP BY WAREHOUSE_NAME, QUERY_TYPE
            """,
            
            "costly_queries": """
                SELECT
                    QUERY_ID,
                    ANY_VALUE(QUERY_TEXT) AS QUERY_TEXT,
                    SUM(CREDITS_USED * CREDIT_PRICE) AS QUERY_COST
                FROM METERING_HISTORY
                WHERE USER_NAME = '{user_id}'
                {{date_filter}}
                GROUP BY QUERY_ID
                ORDER BY QUERY_COST DESC
                LIMIT 10
            """,
            
            "long_running_queries": """
                SELECT
                    QUERY_TEXT,
                    USER_NAME,
                    EXECUTION_TIME / 60000 AS EXECUTION_MIN,
                    CREDITS_USED * CREDIT_PRICE AS CREDITS_USED
                FROM QUERY_HISTORY
                WHERE USER_NAME = '{user_id}'
                AND EXECUTION_TIME > 300000  -- 5+ minutes
                {{date_filter}}
                ORDER BY EXECUTION_TIME DESC
                LIMIT 10
            """
        }
    
    def run_query(self, key: str, date_range: str = "7d", user_id: Optional[str] = None) -> Any:
        # Add user_id formatting
        if user_id and '{user_id}' in self._queries[key]:
            raw_query = self._queries[key].format(user_id=user_id)
        else:
            raw_query = self._queries[key]
        
        # Rest of method remains same...
