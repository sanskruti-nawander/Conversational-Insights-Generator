import asyncpg
from typing import Optional

from .config import DATABASE_URL


class DB:
    pool: Optional[asyncpg.pool.Pool] = None


db = DB()


async def init_db() -> None:
    if db.pool is not None:
        return

    db.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    async with db.pool.acquire() as conn:
        # Original table
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

        # New extended analysis table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS call_records_extended (
                id SERIAL PRIMARY KEY,
                transcript TEXT NOT NULL,

                customer_intent TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                action_required BOOLEAN NOT NULL,
                summary TEXT NOT NULL,

                primary_purpose TEXT NOT NULL,
                objective_met BOOLEAN NOT NULL,
                key_results TEXT NOT NULL, -- stored as joined string
                customer_intentions TEXT NOT NULL,
                circumstances TEXT NOT NULL,
                reasons_non_payment TEXT,
                financial_hardship TEXT,
                start_sentiment TEXT NOT NULL,
                end_sentiment TEXT NOT NULL,
                agent_performance_rating INT NOT NULL,
                agent_performance_notes TEXT NOT NULL,

                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
