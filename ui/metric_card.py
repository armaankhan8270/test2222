# src/finops_framework/ui/metric_card.py

import streamlit as st
from typing import Union, Optional, Dict, Any
import inspect # To dynamically get functions from helpers

# Import helper functions for custom formatting
from finops_framework.utils import helpers

def render_metric_card(
    label: str,
    value: Union[int, float, str, None],
    delta: Union[int, float, None] = None,
    format_value: str = "{:,.0f}",
    format_delta: str = "{:+.2%}",
    formatter_func: Optional[str] = None, # Name of a helper function to call for value formatting
    help_text: Optional[str] = None,
    theme_config: Dict[str, Any] = None
):
    """
    Renders a Streamlit metric card with customizable formatting and delta calculation.

    Args:
        label (str): The label for the metric card.
        value (Union[int, float, str, None]): The main value to display.
        delta (Union[int, float, None], optional): The delta value for comparison. Defaults to None.
        format_value (str): F-string format for the main value. Defaults to "{:,.0f}".
        format_delta (str): F-string format for the delta. Defaults to "{:+.2%}".
        formatter_func (Optional[str]): The name of a helper function from `finops_framework.utils.helpers`
                                        to apply for custom value formatting (e.g., "format_bytes").
                                        If provided, `format_value` will be passed as an argument to it.
        help_text (Optional[str]): Tooltip text for the metric. Defaults to None.
        theme_config (Dict[str, Any], optional): Dictionary containing theme configuration,
                                                used for delta colors. Defaults to None.
    """
    display_value: str
    display_delta: Optional[str] = None
    delta_color: Optional[str] = None

    # Apply custom formatter function if specified
    if formatter_func:
        if hasattr(helpers, formatter_func) and inspect.isfunction(getattr(helpers, formatter_func)):
            try:
                # Dynamically get the function and call it
                formatter = getattr(helpers, formatter_func)
                # Pass format_value as a potential decimal_places arg if it's numeric format
                # This is a bit of a hack, but common in config-driven formatting
                if isinstance(value, (int, float)) and "decimal_places" in inspect.signature(formatter).parameters:
                     # Extract decimal places from format_value string, if possible. e.g., "{:,.2f}" -> 2
                    try:
                        decimal_places = int(format_value.split('.')[-1][0])
                        display_value = formatter(value, decimal_places=decimal_places)
                    except (ValueError, IndexError):
                        display_value = formatter(value) # Fallback if format_value not parseable
                else:
                    display_value = formatter(value)
            except Exception as e:
                st.warning(f"Error applying formatter_func '{formatter_func}' to value '{value}': {e}. Displaying raw value.")
                display_value = str(value) if value is not None else "N/A"
        else:
            st.warning(f"Formatter function '{formatter_func}' not found in helpers. Using default format.")
            display_value = format_value.format(value) if value is not None else "N/A"
    else:
        display_value = format_value.format(value) if value is not None else "N/A"


    # Handle delta display and color
    if delta is not None:
        try:
            # Use calculate_delta_percentage from helpers for consistent delta logic
            delta_percentage = helpers.calculate_delta_percentage(value, delta)

            if delta_percentage is not None:
                display_delta = format_delta.format(delta_percentage)

                if theme_config:
                    if delta_percentage > 0:
                        delta_color = "inverse" # Red for positive cost, green for negative
                    elif delta_percentage < 0:
                        delta_color = "normal" # Green for negative cost, red for positive
                    else:
                        delta_color = "off" # Grey for no change
            else:
                display_delta = "N/A" # For cases like division by zero in calculate_delta_percentage
        except Exception as e:
            st.warning(f"Error processing delta for '{label}': {e}. Delta will not be displayed.")
            display_delta = None
    
    # Render the Streamlit metric
    st.metric(label=label, value=display_value, delta=display_delta, delta_color=delta_color, help=help_text)