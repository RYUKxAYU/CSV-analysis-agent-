import pandas as pd
import io
from db.queries.files import get_file_by_id
from core.gcs import download_from_gcs
from typing import Optional

# In-memory cache: file_id → DataFrame (lives for process lifetime)
_df_cache: dict[str, pd.DataFrame] = {}


async def get_dataframe(file_id: str) -> pd.DataFrame:
    """Resolve file_id → download from GCS → return DataFrame. Cached after first load."""
    if file_id in _df_cache:
        return _df_cache[file_id]

    file_record = await get_file_by_id(file_id)
    if not file_record:
        raise FileNotFoundError(f"No file found for id: {file_id}")

    # If using GCS, download from cloud
    if file_record.get("gcs_object_name"):
        content_bytes = await download_from_gcs(file_record["gcs_object_name"])
        if file_record["original_name"].endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content_bytes))
        else:
            df = pd.read_excel(io.BytesIO(content_bytes))
    else:
        # Local storage fallback - load from storage_path
        storage_path = file_record["storage_path"]
        if storage_path.startswith("local://"):
            local_path = storage_path.replace("local://", "")
            if file_record["original_name"].endswith(".csv"):
                df = pd.read_csv(local_path)
            else:
                df = pd.read_excel(local_path)
        else:
            raise ValueError(f"Unknown storage type: {storage_path}")

    _df_cache[file_id] = df
    return df


def evict_cache(file_id: str):
    """Call this when a session/file is deleted."""
    _df_cache.pop(file_id, None)


def get_cached_dataframe(file_id: str) -> Optional[pd.DataFrame]:
    """Get cached DataFrame without loading from storage."""
    return _df_cache.get(file_id)