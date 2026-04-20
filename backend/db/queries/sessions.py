from db.connection import get_pool
from typing import Optional


async def create_session(user_id: str, file_id: str = None, title: str = None) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO sessions (user_id, file_id, title)
            VALUES ($1, $2, $3)
            RETURNING *
        """, user_id, file_id, title)
        return dict(row)


async def get_session_by_id(session_id: str, user_id: str) -> Optional[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM sessions WHERE id = $1 AND user_id = $2", session_id, user_id
        )
        return dict(row) if row else None


async def get_session_with_file(session_id: str, user_id: str) -> Optional[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT s.*, f.original_name, f.storage_path, f.gcs_object_name, f.column_names
            FROM sessions s
            LEFT JOIN uploaded_files f ON s.file_id = f.id
            WHERE s.id = $1 AND s.user_id = $2
        """, session_id, user_id)
        return dict(row) if row else None


async def get_user_sessions(user_id: str) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT s.*, f.original_name
            FROM sessions s
            LEFT JOIN uploaded_files f ON s.file_id = f.id
            WHERE s.user_id = $1
            ORDER BY s.last_active_at DESC
        """, user_id)
        return [dict(row) for row in rows]


async def update_session_title(session_id: str, title: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE sessions SET title = $1, last_active_at = NOW() WHERE id = $2",
            title, session_id
        )


async def update_session_activity(session_id: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE sessions SET last_active_at = NOW() WHERE id = $1", session_id
        )


async def delete_session(session_id: str, user_id: str) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM sessions WHERE id = $1 AND user_id = $2", session_id, user_id
        )
        return result == "DELETE 1"


async def save_message(session_id: str, role: str, content: str) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO messages (session_id, role, content)
            VALUES ($1, $2, $3)
            RETURNING *
        """, session_id, role, content)
        return dict(row)


async def get_chat_history(session_id: str, limit: int = 10) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT role, content FROM messages 
            WHERE session_id = $1 
            ORDER BY created_at ASC 
            LIMIT $2
        """, session_id, limit)
        return [dict(row) for row in rows]