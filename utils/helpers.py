# src/finops_framework/utils/helpers.py

from typing import Optional, Union, Dict, Any
import math

def format_currency(value: Union[int, float, None], currency_symbol: str = "$", decimal_places: int = 2) -> str:
    """
    Formats a numeric value as currency.

    Args:
        value (Union[int, float, None]): The numeric value to format. Can be None.
        currency_symbol (str): The symbol for the currency (e.g., "$", "€").
        decimal_places (int): Number of decimal places for the formatted value.

    Returns:
        str: The formatted currency string, or "N/A" if value is None.
    """
    if value is None or math.isnan(value):
        return "N/A"
    return f"{currency_symbol}{value:,.{decimal_places}f}"

def format_percentage(value: Union[int, float, None], decimal_places: int = 1) -> str:
    """
    Formats a numeric value as a percentage.

    Args:
        value (Union[int, float, None]): The numeric value to format (e.g., 0.15 for 15%). Can be None.
        decimal_places (int): Number of decimal places for the percentage.

    Returns:
        str: The formatted percentage string, or "N/A" if value is None.
    """
    if value is None or math.isnan(value):
        return "N/A"
    return f"{value:.{decimal_places}%}"

def calculate_delta_percentage(current_value: Union[int, float, None], previous_value: Union[int, float, None]) -> Optional[float]:
    """
    Calculates the percentage change between a current and a previous value.

    Args:
        current_value (Union[int, float, None]): The current value.
        previous_value (Union[int, float, None]): The previous value.

    Returns:
        Optional[float]: The percentage change (e.g., 0.1 for +10%), or None if calculation is not possible.
    """
    if current_value is None or previous_value is None or math.isnan(current_value) or math.isnan(previous_value):
        return None
    if previous_value == 0:
        return 0.0 if current_value == 0 else None # Avoid division by zero, return 0 if both are 0, else None
    return (current_value - previous_value) / previous_value

def format_bytes(bytes_value: Union[int, float, None], unit: str = "GB", decimal_places: int = 2) -> str:
    """
    Formats a byte value into a human-readable unit (KB, MB, GB, TB).

    Args:
        bytes_value (Union[int, float, None]): The value in bytes. Can be None.
        unit (str): The desired unit ('KB', 'MB', 'GB', 'TB'). Case-insensitive.
        decimal_places (int): Number of decimal places.

    Returns:
        str: Formatted string with unit, or "N/A" if value is None.
    """
    if bytes_value is None or math.isnan(bytes_value):
        return "N/A"

    units = {"KB": 1, "MB": 2, "GB": 3, "TB": 4}
    if unit.upper() not in units:
        raise ValueError(f"Invalid unit. Choose from {', '.join(units.keys())}")

    power = units[unit.upper()]
    converted_value = bytes_value / (1024 ** power)
    return f"{converted_value:,.{decimal_places}f} {unit.upper()}"

def format_duration_seconds(seconds: Union[int, float, None], decimal_places: int = 1) -> str:
    """
    Formats a duration in seconds into a human-readable string (e.g., "1m 30s").

    Args:
        seconds (Union[int, float, None]): The duration in seconds. Can be None.
        decimal_places (int): Number of decimal places for seconds.

    Returns:
        str: Formatted duration string, or "N/A" if value is None.
    """
    if seconds is None or math.isnan(seconds):
        return "N/A"
    
    seconds = int(round(seconds)) # Round to nearest second for cleaner display

    if seconds < 60:
        return f"{seconds:.{decimal_places}f}s"
    
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.{decimal_places}f}s"
    
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{int(hours)}h {int(minutes)}m {seconds:.{decimal_places}f}s"
    
    days, hours = divmod(hours, 24)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {seconds:.{decimal_places}f}s"