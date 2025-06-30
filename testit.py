# query_store.py
"""Centralized query store for all Snowflake queries with templating support."""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class QueryStore:
    """Centralized store for all Snowflake queries with dynamic filtering."""
    
    QUERIES: Dict[str, str] = {
        # User Metrics
        "total_users": """
            SELECT COUNT(DISTINCT user_name) as total_users
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            {user_filter}
        """,
        
        "active_users": """
            SELECT COUNT(DISTINCT user_name) as active_users
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            AND start_time >= CURRENT_DATE - 7
            {user_filter}
        """,
        
        "total_queries": """
            SELECT COUNT(*) as total_queries
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            {user_filter}
        """,
        
        "avg_query_duration": """
            SELECT ROUND(AVG(total_elapsed_time)/1000, 2) as avg_duration_seconds
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            AND total_elapsed_time > 0
            {user_filter}
        """,
        
        "total_compute_cost": """
            SELECT ROUND(SUM(credits_used * 3.0), 2) as total_cost_usd
            FROM snowflake.account_usage.warehouse_metering_history
            WHERE start_time >= '{start_date}'
        """,
        
        # Chart Queries
        "cost_by_user": """
            SELECT 
                q.user_name,
                ROUND(SUM(w.credits_used * 3.0), 2) as cost_usd,
                COUNT(q.query_id) as query_count
            FROM snowflake.account_usage.query_history q
            JOIN snowflake.account_usage.warehouse_metering_history w
                ON DATE(q.start_time) = DATE(w.start_time)
                AND q.warehouse_name = w.warehouse_name
            WHERE q.start_time >= '{start_date}'
            {user_filter}
            GROUP BY q.user_name
            ORDER BY cost_usd DESC
            LIMIT 20
        """,
        
        "queries_over_time": """
            SELECT 
                DATE(start_time) as query_date,
                COUNT(*) as query_count,
                COUNT(DISTINCT user_name) as unique_users,
                ROUND(AVG(total_elapsed_time)/1000, 2) as avg_duration
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            {user_filter}
            GROUP BY DATE(start_time)
            ORDER BY query_date
        """,
        
        "warehouse_usage": """
            SELECT 
                warehouse_name,
                ROUND(SUM(credits_used), 2) as total_credits,
                ROUND(SUM(credits_used * 3.0), 2) as total_cost_usd,
                COUNT(DISTINCT DATE(start_time)) as active_days
            FROM snowflake.account_usage.warehouse_metering_history
            WHERE start_time >= '{start_date}'
            GROUP BY warehouse_name
            ORDER BY total_credits DESC
        """,
        
        "longest_queries": """
            SELECT 
                query_id,
                user_name,
                warehouse_name,
                ROUND(total_elapsed_time/1000, 2) as duration_seconds,
                ROUND(total_elapsed_time/60000, 2) as duration_minutes,
                start_time,
                LEFT(query_text, 100) as query_preview
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            AND total_elapsed_time > 0
            {user_filter}
            ORDER BY total_elapsed_time DESC
            LIMIT 10
        """,
        
        "storage_usage": """
            SELECT 
                DATE(usage_date) as usage_date,
                ROUND(storage_bytes/1024/1024/1024, 2) as storage_gb,
                ROUND(stage_bytes/1024/1024/1024, 2) as stage_gb,
                ROUND(failsafe_bytes/1024/1024/1024, 2) as failsafe_gb
            FROM snowflake.account_usage.storage_usage
            WHERE usage_date >= '{start_date}'
            ORDER BY usage_date
        """,
        
        "query_types": """
            SELECT 
                query_type,
                COUNT(*) as query_count,
                ROUND(AVG(total_elapsed_time)/1000, 2) as avg_duration,
                ROUND(SUM(total_elapsed_time)/1000, 2) as total_duration
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            AND query_type IS NOT NULL
            {user_filter}
            GROUP BY query_type
            ORDER BY query_count DESC
        """,
        
        "hourly_usage": """
            SELECT 
                HOUR(start_time) as hour_of_day,
                COUNT(*) as query_count,
                COUNT(DISTINCT user_name) as unique_users,
                ROUND(AVG(total_elapsed_time)/1000, 2) as avg_duration
            FROM snowflake.account_usage.query_history
            WHERE start_time >= '{start_date}'
            {user_filter}
            GROUP BY HOUR(start_time)
            ORDER BY hour_of_day
        """
    }
    
    @staticmethod
    def get_query(query_key: str, start_date: str, user_filter: Optional[str] = None) -> str:
        """Get formatted query with filters applied."""
        if query_key not in QueryStore.QUERIES:
            raise ValueError(f"Query key '{query_key}' not found in QueryStore")
        
        user_filter_clause = ""
        if user_filter:
            user_filter_clause = f"AND user_name = '{user_filter}'"
        
        query = QueryStore.QUERIES[query_key].format(
            start_date=start_date,
            user_filter=user_filter_clause
        )
        
        logger.info(f"Generated query for key: {query_key}")
        return query.strip()
    
    @staticmethod
    def list_queries() -> list:
        """List all available query keys."""
        return list(QueryStore.QUERIES.keys())


# filters.py
"""Date and user filter utilities."""

from datetime import datetime, timedelta
from typing import Tuple, List
import streamlit as st

class FilterHandler:
    """Handle date and user filters for queries."""
    
    DATE_RANGES = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 3 Months": 90,
        "Last 6 Months": 180,
        "Last 9 Months": 270,
        "Last 1 Year": 365
    }
    
    @staticmethod
    def get_date_filter() -> str:
        """Get date filter selection and return SQL date string."""
        col1, col2 = st.columns(2)
        
        with col1:
            date_range = st.selectbox(
                "📅 Select Date Range",
                options=list(FilterHandler.DATE_RANGES.keys()),
                index=1  # Default to Last 30 Days
            )
        
        days_back = FilterHandler.DATE_RANGES[date_range]
        start_date = datetime.now() - timedelta(days=days_back)
        return start_date.strftime("%Y-%m-%d")
    
    @staticmethod
    def get_user_filter(session) -> str:
        """Get user filter selection."""
        try:
            # Get list of users from last 30 days
            users_query = """
                SELECT DISTINCT user_name
                FROM snowflake.account_usage.query_history
                WHERE start_time >= CURRENT_DATE - 30
                ORDER BY user_name
            """
            result = session.sql(users_query).collect()
            users = ["All Users"] + [row[0] for row in result if row[0]]
            
            col1, col2 = st.columns(2)
            with col2:
                selected_user = st.selectbox(
                    "👤 Select User",
                    options=users,
                    index=0
                )
            
            return None if selected_user == "All Users" else selected_user
            
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return None


# chart_renderer.py
"""Chart rendering utilities using Plotly."""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ChartRenderer:
    """Render different types of charts from query results."""
    
    @staticmethod
    def render_chart(
        session,
        query_key: str,
        chart_type: str,
        title: str,
        start_date: str,
        user_filter: Optional[str] = None,
        **kwargs
    ) -> None:
        """Render chart based on query key and chart type."""
        try:
            from query_store import QueryStore
            
            # Get and execute query
            query = QueryStore.get_query(query_key, start_date, user_filter)
            result = session.sql(query).collect()
            
            if not result:
                st.warning(f"No data found for {title}")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            
            # Render based on chart type
            if chart_type == "bar":
                ChartRenderer._render_bar_chart(df, title, **kwargs)
            elif chart_type == "line":
                ChartRenderer._render_line_chart(df, title, **kwargs)
            elif chart_type == "pie":
                ChartRenderer._render_pie_chart(df, title, **kwargs)
            elif chart_type == "area":
                ChartRenderer._render_area_chart(df, title, **kwargs)
            elif chart_type == "scatter":
                ChartRenderer._render_scatter_chart(df, title, **kwargs)
            elif chart_type == "heatmap":
                ChartRenderer._render_heatmap(df, title, **kwargs)
            else:
                st.error(f"Unsupported chart type: {chart_type}")
                
        except Exception as e:
            logger.error(f"Error rendering chart {query_key}: {str(e)}")
            st.error(f"Error rendering {title}: {str(e)}")
    
    @staticmethod
    def _render_bar_chart(df: pd.DataFrame, title: str, **kwargs) -> None:
        """Render bar chart."""
        x_col = kwargs.get('x_col', df.columns[0])
        y_col = kwargs.get('y_col', df.columns[1])
        
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color=y_col,
            color_continuous_scale="Blues"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_line_chart(df: pd.DataFrame, title: str, **kwargs) -> None:
        """Render line chart."""
        x_col = kwargs.get('x_col', df.columns[0])
        y_cols = kwargs.get('y_cols', [df.columns[1]])
        
        fig = go.Figure()
        for y_col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_col.replace('_', ' ').title()
            ))
        
        fig.update_layout(title=title, xaxis_title=x_col, yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_pie_chart(df: pd.DataFrame, title: str, **kwargs) -> None:
        """Render pie chart."""
        labels_col = kwargs.get('labels_col', df.columns[0])
        values_col = kwargs.get('values_col', df.columns[1])
        
        fig = px.pie(
            df,
            values=values_col,
            names=labels_col,
            title=title
        )
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_area_chart(df: pd.DataFrame, title: str, **kwargs) -> None:
        """Render area chart."""
        x_col = kwargs.get('x_col', df.columns[0])
        y_cols = kwargs.get('y_cols', [df.columns[1]])
        
        fig = go.Figure()
        for y_col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                fill='tonexty' if len(y_cols) > 1 else 'tozeroy',
                mode='lines',
                name=y_col.replace('_', ' ').title()
            ))
        
        fig.update_layout(title=title)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_scatter_chart(df: pd.DataFrame, title: str, **kwargs) -> None:
        """Render scatter chart."""
        x_col = kwargs.get('x_col', df.columns[0])
        y_col = kwargs.get('y_col', df.columns[1])
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color=y_col,
            size=y_col
        )
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_heatmap(df: pd.DataFrame, title: str, **kwargs) -> None:
        """Render heatmap."""
        x_col = kwargs.get('x_col', df.columns[0])
        y_col = kwargs.get('y_col', df.columns[1])
        z_col = kwargs.get('z_col', df.columns[2])
        
        # Pivot data for heatmap
        pivot_df = df.pivot(index=y_col, columns=x_col, values=z_col)
        
        fig = px.imshow(
            pivot_df,
            title=title,
            aspect="auto",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)


# metric_renderer.py
"""Metric card rendering utilities."""

import streamlit as st
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

class MetricRenderer:
    """Render metric cards from query results."""
    
    @staticmethod
    def render_metric(
        session,
        query_key: str,
        label: str,
        start_date: str,
        user_filter: Optional[str] = None,
        icon: str = "📊",
        format_type: str = "number",
        delta_query_key: Optional[str] = None
    ) -> None:
        """Render a metric card."""
        try:
            from query_store import QueryStore
            
            # Get and execute main query
            query = QueryStore.get_query(query_key, start_date, user_filter)
            result = session.sql(query).collect()
            
            if not result or not result[0]:
                st.metric(label=f"{icon} {label}", value="No Data")
                return
            
            # Get main value
            main_value = result[0][0]
            
            # Format value
            formatted_value = MetricRenderer._format_value(main_value, format_type)
            
            # Get delta if specified
            delta = None
            if delta_query_key:
                delta = MetricRenderer._get_delta(
                    session, delta_query_key, start_date, user_filter
                )
            
            # Render metric
            st.metric(
                label=f"{icon} {label}",
                value=formatted_value,
                delta=delta
            )
            
        except Exception as e:
            logger.error(f"Error rendering metric {query_key}: {str(e)}")
            st.metric(label=f"{icon} {label}", value="Error")
    
    @staticmethod
    def _format_value(value: Union[int, float], format_type: str) -> str:
        """Format metric value based on type."""
        if value is None:
            return "N/A"
        
        if format_type == "currency":
            return f"${value:,.2f}"
        elif format_type == "percentage":
            return f"{value:.1f}%"
        elif format_type == "duration":
            return f"{value:.1f}s"
        elif format_type == "number":
            if isinstance(value, float):
                return f"{value:,.1f}"
            return f"{value:,}"
        else:
            return str(value)
    
    @staticmethod
    def _get_delta(
        session, 
        delta_query_key: str, 
        start_date: str, 
        user_filter: Optional[str]
    ) -> Optional[str]:
        """Get delta value for comparison."""
        try:
            from query_store import QueryStore
            
            query = QueryStore.get_query(delta_query_key, start_date, user_filter)
            result = session.sql(query).collect()
            
            if result and result[0]:
                return f"{result[0][0]:.1f}%"
            return None
            
        except Exception as e:
            logger.error(f"Error getting delta: {str(e)}")
            return None


# utils.py
"""Utility functions for error handling and caching."""

import streamlit as st
import hashlib
import pickle
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple cache manager for query results."""
    
    _cache = {}
    
    @staticmethod
    def get_cache_key(query: str, params: dict) -> str:
        """Generate cache key from query and parameters."""
        cache_string = f"{query}_{str(sorted(params.items()))}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    @staticmethod
    def get_from_cache(cache_key: str) -> Any:
        """Get value from cache."""
        return CacheManager._cache.get(cache_key)
    
    @staticmethod
    def set_cache(cache_key: str, value: Any) -> None:
        """Set value in cache."""
        CacheManager._cache[cache_key] = value
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cache."""
        CacheManager._cache.clear()


def handle_errors(func: Callable) -> Callable:
    """Decorator for error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
            return None
    return wrapper


def init_logging():
    """Initialize logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


# user_360_page.py
"""User 360 Dashboard Page - Demo implementation."""

import streamlit as st
from chart_renderer import ChartRenderer
from metric_renderer import MetricRenderer
from filters import FilterHandler
from utils import init_logging

# Initialize logging
init_logging()

def render_user_360_page(session):
    """Render the User 360 dashboard page."""
    
    st.title("🎯 User 360 Dashboard")
    st.markdown("### Comprehensive view of Snowflake user activity and costs")
    
    # Filters Section
    st.markdown("---")
    st.subheader("🔍 Filters")
    
    start_date = FilterHandler.get_date_filter()
    user_filter = FilterHandler.get_user_filter(session)
    
    # Metrics Section
    st.markdown("---")
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        MetricRenderer.render_metric(
            session=session,
            query_key="total_users",
            label="Total Users",
            start_date=start_date,
            user_filter=user_filter,
            icon="👥",
            format_type="number"
        )
    
    with col2:
        MetricRenderer.render_metric(
            session=session,
            query_key="total_queries",
            label="Total Queries",
            start_date=start_date,
            user_filter=user_filter,
            icon="⚡",
            format_type="number"
        )
    
    with col3:
        MetricRenderer.render_metric(
            session=session,
            query_key="avg_query_duration",
            label="Avg Query Duration",
            start_date=start_date,
            user_filter=user_filter,
            icon="⏱️",
            format_type="duration"
        )
    
    with col4:
        MetricRenderer.render_metric(
            session=session,
            query_key="total_compute_cost",
            label="Total Compute Cost",
            start_date=start_date,
            user_filter=user_filter,
            icon="💰",
            format_type="currency"
        )
    
    with col5:
        MetricRenderer.render_metric(
            session=session,
            query_key="active_users",
            label="Active Users (7d)",
            start_date=start_date,
            user_filter=user_filter,
            icon="🔥",
            format_type="number"
        )
    
    # Charts Section
    st.markdown("---")
    st.subheader("📈 Analytics")
    
    # Row 1: Cost Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        ChartRenderer.render_chart(
            session=session,
            query_key="cost_by_user",
            chart_type="bar",
            title="💸 Cost by User",
            start_date=start_date,
            user_filter=user_filter,
            x_col="USER_NAME",
            y_col="COST_USD"
        )
    
    with col2:
        ChartRenderer.render_chart(
            session=session,
            query_key="warehouse_usage",
            chart_type="pie",
            title="🏭 Warehouse Usage Distribution",
            start_date=start_date,
            user_filter=user_filter,
            labels_col="WAREHOUSE_NAME",
            values_col="TOTAL_COST_USD"
        )
    
    # Row 2: Query Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        ChartRenderer.render_chart(
            session=session,
            query_key="queries_over_time",
            chart_type="line",
            title="📊 Query Activity Over Time",
            start_date=start_date,
            user_filter=user_filter,
            x_col="QUERY_DATE",
            y_cols=["QUERY_COUNT", "UNIQUE_USERS"]
        )
    
    with col2:
        ChartRenderer.render_chart(
            session=session,
            query_key="query_types",
            chart_type="bar",
            title="🔍 Query Types Distribution",
            start_date=start_date,
            user_filter=user_filter,
            x_col="QUERY_TYPE",
            y_col="QUERY_COUNT"
        )
    
    # Row 3: Performance Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        ChartRenderer.render_chart(
            session=session,
            query_key="hourly_usage",
            chart_type="bar",
            title="⏰ Hourly Usage Pattern",
            start_date=start_date,
            user_filter=user_filter,
            x_col="HOUR_OF_DAY",
            y_col="QUERY_COUNT"
        )
    
    with col2:
        ChartRenderer.render_chart(
            session=session,
            query_key="storage_usage",
            chart_type="area",
            title="💾 Storage Usage Trend",
            start_date=start_date,
            user_filter=user_filter,
            x_col="USAGE_DATE",
            y_cols=["STORAGE_GB", "STAGE_GB", "FAILSAFE_GB"]
        )
    
    # Detailed Analysis Table
    st.markdown("---")
    st.subheader("🔍 Longest Running Queries")
    
    try:
        from query_store import QueryStore
        
        query = QueryStore.get_query("longest_queries", start_date, user_filter)
        result = session.sql(query).collect()
        
        if result:
            import pandas as pd
            df = pd.DataFrame(result)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No long-running queries found for the selected period.")
            
    except Exception as e:
        st.error(f"Error loading query details: {str(e)}")
    
    # Insights Section
    st.markdown("---")
    st.subheader("💡 Key Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Cost Optimization Tips:**
        - Monitor users with highest costs
        - Identify idle warehouses
        - Optimize query patterns
        - Consider warehouse auto-suspend
        """)
    
    with col2:
        st.success("""
        **Performance Improvements:**
        - Review long-running queries
        - Optimize during peak hours
        - Consider query caching
        - Monitor storage growth
        """)


# main.py
"""Main application entry point."""

import streamlit as st
from snowflake.snowpark.context import get_active_session
from user_360_page import render_user_360_page

def main():
    """Main application function."""
    
    st.set_page_config(
        page_title="Snowflake FinOps Dashboard",
        page_icon="❄️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    try:
        # Get Snowflake session
        session = get_active_session()
        
        # Render the User 360 dashboard
        render_user_360_page(session)
        
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        st.info("Please ensure you're running this in a Snowflake environment with proper session context.")


if __name__ == "__main__":
    main()





QUERIES: Dict[str, str] = {
    # User Metrics
    "total_users": """
        SELECT COUNT(DISTINCT user_name) AS total_users
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
        {user_filter}
    """,

    "active_users": """
        SELECT COUNT(DISTINCT user_name) AS active_users
        FROM snowflake.account_usage.query_history
        WHERE start_time >= CURRENT_DATE - 7
        {user_filter}
    """,

    "total_queries": """
        SELECT COUNT(*) AS total_queries
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
        {user_filter}
    """,

    "avg_query_duration": """
        SELECT ROUND(AVG(total_elapsed_time) / 1000, 2) AS avg_duration_seconds
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
          AND total_elapsed_time > 0
        {user_filter}
    """,

    "total_compute_cost": """
        SELECT ROUND(SUM(credits_used * 3.0), 2) AS total_cost_usd
        FROM snowflake.account_usage.warehouse_metering_history
        WHERE start_time >= '{start_date}'
    """,

    # Chart Queries
    "cost_by_user": """
        SELECT 
            q.user_name,
            ROUND(SUM(w.credits_used * 3.0) / COUNT(DISTINCT w.start_time), 2) AS estimated_cost_usd,
            COUNT(q.query_id) AS query_count
        FROM snowflake.account_usage.query_history q
        JOIN snowflake.account_usage.warehouse_metering_history w
            ON DATE_TRUNC('DAY', q.start_time) = DATE_TRUNC('DAY', w.start_time)
           AND q.warehouse_name = w.warehouse_name
        WHERE q.start_time >= '{start_date}'
        {user_filter}
        GROUP BY q.user_name
        ORDER BY estimated_cost_usd DESC
        LIMIT 20
    """,

    "queries_over_time": """
        SELECT 
            DATE(start_time) AS query_date,
            COUNT(*) AS query_count,
            COUNT(DISTINCT user_name) AS unique_users,
            ROUND(AVG(total_elapsed_time) / 1000, 2) AS avg_duration
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
        {user_filter}
        GROUP BY DATE(start_time)
        ORDER BY query_date
    """,

    "warehouse_usage": """
        SELECT 
            warehouse_name,
            ROUND(SUM(credits_used), 2) AS total_credits,
            ROUND(SUM(credits_used * 3.0), 2) AS total_cost_usd,
            COUNT(DISTINCT DATE(start_time)) AS active_days
        FROM snowflake.account_usage.warehouse_metering_history
        WHERE start_time >= '{start_date}'
        GROUP BY warehouse_name
        ORDER BY total_credits DESC
    """,

    "longest_queries": """
        SELECT 
            query_id,
            user_name,
            warehouse_name,
            ROUND(total_elapsed_time / 1000, 2) AS duration_seconds,
            ROUND(total_elapsed_time / 60000, 2) AS duration_minutes,
            start_time,
            LEFT(query_text, 100) AS query_preview
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
          AND total_elapsed_time > 0
        {user_filter}
        ORDER BY total_elapsed_time DESC
        LIMIT 10
    """,

    "storage_usage": """
        SELECT 
            usage_date,
            ROUND(storage_bytes / 1024 / 1024 / 1024, 2) AS storage_gb,
            ROUND(stage_bytes / 1024 / 1024 / 1024, 2) AS stage_gb,
            ROUND(failsafe_bytes / 1024 / 1024 / 1024, 2) AS failsafe_gb
        FROM snowflake.account_usage.storage_usage
        WHERE usage_date >= '{start_date}'
        ORDER BY usage_date
    """,

    "query_types": """
        SELECT 
            query_type,
            COUNT(*) AS query_count,
            ROUND(AVG(total_elapsed_time) / 1000, 2) AS avg_duration,
            ROUND(SUM(total_elapsed_time) / 1000, 2) AS total_duration
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
          AND query_type IS NOT NULL
        {user_filter}
        GROUP BY query_type
        ORDER BY query_count DESC
    """,

    "hourly_usage": """
        SELECT 
            EXTRACT(HOUR FROM start_time) AS hour_of_day,
            COUNT(*) AS query_count,
            COUNT(DISTINCT user_name) AS unique_users,
            ROUND(AVG(total_elapsed_time) / 1000, 2) AS avg_duration
        FROM snowflake.account_usage.query_history
        WHERE start_time >= '{start_date}'
        {user_filter}
        GROUP BY EXTRACT(HOUR FROM start_time)
        ORDER BY hour_of_day
    """
}
