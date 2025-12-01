import asyncpg
from typing import Optional

from .config import DATABASE_URL


class DB:
    pool: Optional[asyncpg.pool.Pool] = None


db = DB()


async def init_db() -> None:
    """
    Initialize connection pool and create table if needed.
    """
    if db.pool is not None:
        return

    db.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    async with db.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS call_records (
                id SERIAL PRIMARY KEY,
                transcript TEXT NOT NULL,
                intent TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                action_required BOOLEAN NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
