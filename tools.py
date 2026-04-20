import os
import pandas as pd
from langchain_core.tools import tool

@tool
def read_notebook(filepath: str) -> str:
    """Read the contents of a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Contents of '{filepath}':\n{content}"
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_notebook(filepath: str, content: str) -> str:
    """Write content to a text file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}'."
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@tool
def query_csv(filepath: str) -> str:
    """Analyze a CSV file and return its structure and first few rows."""
    try:
        df = pd.read_csv(filepath)
        description = f"CSV '{filepath}' loaded successfully.\n"
        description += f"Columns: {list(df.columns)}\n"
        description += f"Sample Data:\n{df.head(3).to_string()}"
        return description
    except Exception as e:
        return f"Error reading CSV: {str(e)}"
