"""
Visualization utilities for formatting Plotly figures.
Ensures consistent JSON output for frontend rendering.
"""
import json
from typing import Union


def format_plotly_json(fig) -> str:
    """
    Convert a Plotly figure to a JSON string for frontend rendering.
    
    Args:
        fig: A Plotly figure object (go.Figure or px figure)
        
    Returns:
        JSON string representation of the figure
    """
    return fig.to_json()


def validate_plotly_json(json_str: str) -> bool:
    """
    Validate that a string is valid Plotly JSON.
    
    Args:
        json_str: String to validate
        
    Returns:
        True if valid Plotly JSON, False otherwise
    """
    try:
        data = json.loads(json_str)
        # Plotly JSON should have 'data' and 'layout' keys
        return 'data' in data and 'layout' in data
    except (json.JSONDecodeError, TypeError):
        return False
