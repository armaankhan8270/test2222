# src/finops_framework/ui/chart_renderer.py

import streamlit as st
import pandas as pd
import altair as alt
from typing import Dict, Any, Optional

# --- Helper function to create a base Altair chart ---
def _create_base_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_axis_title: str,
    y_axis_title: str,
    title: str,
    theme_config: Dict[str, Any],
    color_col: Optional[str] = None # For multi-series charts or coloring
) -> alt.Chart:
    """
    Creates a base Altair chart with common properties (title, axes, interactivity).
    """
    base = alt.Chart(data).properties(
        title={
            "text": [title],
            "subtitle": [""], # Placeholder for subtitle if needed later
            "anchor": "start",
            "fontSize": 18,
            "subtitleFontSize": 12,
            "color": theme_config["text_color"],
            "subtitleColor": theme_config["text_color"]
        },
        height=theme_config.get("chart_height", 350) # Use default from theme if not specified
    ).interactive() # Enable zooming and panning

    return base

# --- Chart Type Renderers ---

def _render_line_chart(
    data: pd.DataFrame,
    config: Dict[str, Any],
    theme_config: Dict[str, Any]
):
    """Renders a line chart."""
    x_col = config.get("x_col")
    y_col = config.get("y_col")
    x_axis_title = config.get("x_axis_title", x_col)
    y_axis_title = config.get("y_axis_title", y_col)
    title = config.get("title", "Line Chart")

    # Ensure required columns exist
    if not all(col in data.columns for col in [x_col, y_col]):
        st.warning(f"Missing required columns for line chart '{title}': {x_col}, {y_col}")
        st.dataframe(data) # Show data for debugging
        return

    base = _create_base_chart(data, x_col, y_col, x_axis_title, y_axis_title, title, theme_config)

    chart = base.mark_line(point=True).encode(
        x=alt.X(x_col, axis=alt.Axis(title=x_axis_title)),
        y=alt.Y(y_col, axis=alt.Axis(title=y_axis_title)),
        color=alt.value(theme_config["chart_colors"][0]), # Use first primary color
        tooltip=[alt.Tooltip(x_col, title=x_axis_title), alt.Tooltip(y_col, title=y_axis_title, format=",.2f")]
    ).properties(
        color=theme_config["chart_colors"][0] # Ensure consistent color if not multi-series
    )
    st.altair_chart(chart, use_container_width=True)

def _render_bar_chart(
    data: pd.DataFrame,
    config: Dict[str, Any],
    theme_config: Dict[str, Any]
):
    """Renders a bar chart."""
    x_col = config.get("x_col")
    y_col = config.get("y_col")
    x_axis_title = config.get("x_axis_title", x_col)
    y_axis_title = config.get("y_axis_title", y_col)
    title = config.get("title", "Bar Chart")
    sort_desc = config.get("sort_desc", False) # Default to no sorting

    # Ensure required columns exist
    if not all(col in data.columns for col in [x_col, y_col]):
        st.warning(f"Missing required columns for bar chart '{title}': {x_col}, {y_col}")
        st.dataframe(data)
        return

    base = _create_base_chart(data, x_col, y_col, x_axis_title, y_axis_title, title, theme_config)

    # Apply sorting if specified
    y_encoding = alt.Y(y_col, axis=alt.Axis(title=y_axis_title))
    x_encoding = alt.X(x_col, axis=alt.Axis(title=x_axis_title))

    if sort_desc:
        x_encoding = alt.X(x_col, sort=alt.EncodingSortField(field=y_col, op="sum", order="descending"), axis=alt.Axis(title=x_axis_title))

    chart = base.mark_bar().encode(
        x=x_encoding,
        y=y_encoding,
        color=alt.value(theme_config["chart_colors"][0]), # Use a primary color for all bars
        tooltip=[alt.Tooltip(x_col, title=x_axis_title), alt.Tooltip(y_col, title=y_axis_title, format=",.2f")]
    )
    st.altair_chart(chart, use_container_width=True)

def _render_pie_chart(
    data: pd.DataFrame,
    config: Dict[str, Any],
    theme_config: Dict[str, Any]
):
    """Renders a pie chart."""
    name_col = config.get("name_col") # Column for labels/categories
    value_col = config.get("value_col") # Column for values (e.g., counts, costs)
    title = config.get("title", "Pie Chart")

    if not all(col in data.columns for col in [name_col, value_col]):
        st.warning(f"Missing required columns for pie chart '{title}': {name_col}, {value_col}")
        st.dataframe(data)
        return

    # Calculate percentages for labels
    data_with_percentages = data.copy()
    total = data_with_percentages[value_col].sum()
    if total > 0:
        data_with_percentages['percentage'] = data_with_percentages[value_col] / total
    else:
        data_with_percentages['percentage'] = 0

    base = alt.Chart(data_with_percentages).encode(
        theta=alt.Theta(field="percentage", type="quantitative", stack=True)
    ).properties(
        title={
            "text": [title],
            "anchor": "start",
            "fontSize": 18,
            "color": theme_config["text_color"]
        },
        height=theme_config.get("chart_height", 350)
    )

    pie = base.mark_arc(outerRadius=120).encode( # Outer radius for donut chart effect
        color=alt.Color(name_col, title=name_col, scale=alt.Scale(range=theme_config["chart_colors"])),
        order=alt.Order("percentage", sort="descending"),
        tooltip=[
            alt.Tooltip(name_col, title=name_col),
            alt.Tooltip(value_col, title="Value", format=",.2f"),
            alt.Tooltip("percentage", format=".1%", title="Percentage")
        ]
    )

    text = base.mark_text(radius=140).encode(
        text=alt.Text("percentage", format=".1%"),
        order=alt.Order("percentage", sort="descending"),
        color=alt.value(theme_config["text_color"]) # Set text color to blend with theme
    )

    chart = pie + text
    st.altair_chart(chart, use_container_width=True)

def _render_table(
    data: pd.DataFrame,
    config: Dict[str, Any],
    theme_config: Dict[str, Any] # Not directly used but good for consistency
):
    """Renders a DataFrame as a Streamlit table."""
    title = config.get("title", "Data Table")
    description = config.get("description", "")

    st.markdown(f"**{title}**")
    if description:
        st.caption(description)

    if data.empty:
        st.info(f"No data available for '{title}' in the selected period.")
    else:
        st.dataframe(data, use_container_width=True)


# --- Main Chart Renderer Function ---
def render_chart(
    data: pd.DataFrame,
    chart_config: Dict[str, Any],
    theme_config: Dict[str, Any]
):
    """
    Renders a chart or table based on the provided configuration.

    Args:
        data (pd.DataFrame): The DataFrame containing the chart data.
        chart_config (Dict[str, Any]): Dictionary containing the chart's configuration.
        theme_config (Dict[str, Any]): Dictionary containing the overall app theme.
    """
    if data.empty:
        st.info(f"No data available for '{chart_config.get('title', 'this chart')}' in the selected period.")
        return

    chart_type = chart_config.get("chart_type")

    if chart_type == "line":
        _render_line_chart(data, chart_config, theme_config)
    elif chart_type == "bar":
        _render_bar_chart(data, chart_config, theme_config)
    elif chart_type == "pie":
        _render_pie_chart(data, chart_config, theme_config)
    elif chart_type == "table":
        _render_table(data, chart_config, theme_config)
    else:
        st.warning(f"Unsupported chart type: {chart_type}")
        st.dataframe(data, use_container_width=True) # Fallback to show raw data