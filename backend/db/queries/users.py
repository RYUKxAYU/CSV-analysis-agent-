from db.connection import get_pool
from typing import Optional


async def create_user(email: str, hashed_password: str) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO users (email, hashed_password)
            VALUES ($1, $2)
            RETURNING id, email, created_at, is_active
        """, email, hashed_password)
        return dict(row)


async def get_user_by_email(email: str) -> Optional[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1", email
        )
        return dict(row) if row else None


async def get_user_by_id(user_id: str) -> Optional[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, created_at, is_active FROM users WHERE id = $1", user_id
        )
        return dict(row) if row else None


async def update_user_active(user_id: str, is_active: bool) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_active = $1 WHERE id = $2", is_active, user_id
        )