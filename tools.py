import os
import pandas as pd
from langchain_core.tools import tool

# Global store for uploaded files (populated by the API)
FILE_STORE = {}

def save_file(file_id: str, dataframe):
    """Save a dataframe to the global store."""
    FILE_STORE[file_id] = dataframe

def get_file(file_id: str):
    """Get a dataframe from the global store."""
    return FILE_STORE.get(file_id)

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
        # Check if it's a file_id reference
        if filepath.startswith("file_id:"):
            file_id = filepath.replace("file_id:", "")
            df = get_file(file_id)
            if df is None:
                return f"Error: File with ID '{file_id}' not found in memory."
        else:
            df = pd.read_csv(filepath)
        
        description = f"CSV loaded successfully.\n"
        description += f"Columns: {list(df.columns)}\n"
        description += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
        description += f"\nFirst 5 rows:\n{df.head(5).to_string()}\n"
        description += f"\nData types:\n{df.dtypes.to_string()}"
        return description
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

@tool
def analyze_csv(file_id: str) -> str:
    """Analyze a CSV file using its file_id. Use this when the user provides a file_id."""
    try:
        df = get_file(file_id)
        if df is None:
            return f"Error: File with ID '{file_id}' not found in memory."
        
        description = f"CSV loaded successfully.\n"
        description += f"Columns: {list(df.columns)}\n"
        description += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
        description += f"\nFirst 5 rows:\n{df.head(5).to_string()}\n"
        description += f"\nData types:\n{df.dtypes.to_string()}\n"
        
        # Add basic stats for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            description += f"\nNumeric summary:\n{df[numeric_cols].describe().to_string()}"
        
        return description
    except Exception as e:
        return f"Error analyzing CSV: {str(e)}"