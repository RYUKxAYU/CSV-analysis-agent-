from db.connection import get_pool
from typing import Optional
import uuid


async def create_file_record(data: dict) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO uploaded_files 
                (id, user_id, original_name, storage_path, gcs_object_name, row_count, column_names, file_size_bytes)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8)
            RETURNING *
        """, 
            data["id"], data["user_id"], data["original_name"], data["storage_path"],
            data.get("gcs_object_name"), data.get("row_count"), 
            str(data.get("column_names", [])), data.get("file_size_bytes", 0)
        )
        return dict(row)


async def get_file_by_id(file_id: str) -> Optional[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM uploaded_files WHERE id = $1", file_id
        )
        return dict(row) if row else None


async def get_user_files(user_id: str) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM uploaded_files WHERE user_id = $1 ORDER BY uploaded_at DESC", user_id
        )
        return [dict(row) for row in rows]


async def delete_file(file_id: str, user_id: str) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM uploaded_files WHERE id = $1 AND user_id = $2", file_id, user_id
        )
        return result == "DELETE 1"