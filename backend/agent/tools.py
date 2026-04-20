from langchain.tools import tool
from agent.file_context import get_dataframe, get_cached_dataframe


def build_csv_tools(file_id: str):
    """Returns tools pre-bound to a specific file_id."""
    
    @tool
    async def describe_data(_: str = "") -> str:
        """Returns shape, column names, and data types of the uploaded CSV."""
        df = await get_dataframe(file_id)
        return f"Shape: {df.shape}\nColumns: {list(df.columns)}\nDtypes:\n{df.dtypes.to_string()}"

    @tool
    async def compute_statistics(_: str = "") -> str:
        """Returns statistical summary (mean, median, std, etc.) of numeric columns."""
        df = await get_dataframe(file_id)
        return df.describe().to_string()

    @tool
    async def sample_rows(n: str = "5") -> str:
        """Returns the first N rows of the CSV."""
        df = await get_dataframe(file_id)
        return df.head(int(n)).to_string()

    @tool
    async def filter_and_count(condition: str) -> str:
        """
        Filter rows by a condition and return count + sample.
        Example condition: "Price > 100"
        """
        df = await get_dataframe(file_id)
        try:
            filtered = df.query(condition)
            return f"Matching rows: {len(filtered)}\n{filtered.head(5).to_string()}"
        except Exception as e:
            return f"Filter error: {str(e)}"

    @tool
    async def get_column_values(column: str) -> str:
        """Returns unique values for a specific column."""
        df = await get_dataframe(file_id)
        if column not in df.columns:
            return f"Error: Column '{column}' not found. Available columns: {list(df.columns)}"
        unique_vals = df[column].unique()[:20]
        return f"Unique values in '{column}':\n{', '.join(map(str, unique_vals))}"

    @tool
    async def group_by_column(column: str, agg_column: str = None, agg_func: str = "sum") -> str:
        """
        Group data by a column and aggregate.
        Example: group_by_column('Category', 'Revenue', 'sum')
        """
        df = await get_dataframe(file_id)
        if column not in df.columns:
            return f"Error: Column '{column}' not found"
        
        if agg_column and agg_column in df.columns:
            result = df.groupby(column)[agg_column].agg(agg_func)
        else:
            result = df.groupby(column).size()
        
        return result.to_string()

    return [describe_data, compute_statistics, sample_rows, filter_and_count, get_column_values, group_by_column]