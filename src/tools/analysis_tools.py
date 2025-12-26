"""
Analysis tools for the Data Science Agent System.
Provides SQL query execution and Python REPL for data analysis.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from typing import Optional


# Default database path
DB_PATH = "ecommerce.db"

# Initialize Python REPL
_python_repl = PythonREPL()


@tool
def sql_tool(query: str, db_path: str = DB_PATH) -> str:
    """
    Execute a SQL query against the ecommerce SQLite database.
    Use this tool to extract data before performing analysis.

    Args:
        query: SQL query to execute (SELECT queries only for safety)
        db_path: Path to the SQLite database (default: ecommerce.db)

    Returns:
        Query results as a formatted string (CSV-like format)
    """
    try:
        engine = create_engine(f"sqlite:///{db_path}")

        # Basic SQL injection prevention - only allow SELECT
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            return "Error: Only SELECT queries are allowed for safety."

        df = pd.read_sql(query, engine)

        if df.empty:
            return "Query returned no results."

        # Return as string for LLM processing
        return df.to_string(index=False)

    except Exception as e:
        return f"SQL Error: {str(e)}"


@tool
def python_tool(code: str) -> str:
    """
    Execute Python code for data analysis, statistical tests, and visualization.
    Use this after fetching data with sql_tool.

    Execute Python code for data analysis, statistical tests, and visualization.
    Use this after fetching data with sql_tool.

    IMPORTANT: For visualizations, use matplotlib or seaborn.
    Save the plot to a file named 'plots/plot_TIMESTAMP.png' (use current timestamp).
    PRINT the filename in the format: "IMAGE_GENERATED: plots/plot_TIMESTAMP.png"

    Available libraries:
    - pandas as pd
    - numpy as np
    - scipy.stats for statistical tests
    - sklearn for machine learning
    - plotly.express as px, plotly.graph_objects as go

    Args:
        code: Python code to execute

    Returns:
        Output of the code execution (stdout/result)
    """
    # Pre-import common libraries
    setup_code = """
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg') # Required for Streamlit Cloud
import matplotlib.pyplot as plt
import seaborn as sns
import json
import time
import os

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)
"""

    try:
        # Run setup imports (silent)
        _python_repl.run(setup_code)

        # Run the actual code
        result = _python_repl.run(code)

        if result:
            return result
        else:
            return "Code executed successfully (no output)."

    except Exception as e:
        return f"Python Error: {str(e)}"


def get_sql_tool():
    """Get the SQL tool instance."""
    return sql_tool


def get_python_tool():
    """Get the Python REPL tool instance."""
    return python_tool


def get_all_tools():
    """Get all analysis tools."""
    return [sql_tool, python_tool]
