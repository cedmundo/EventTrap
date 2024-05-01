import logging

import asyncpg
from fastapi import HTTPException

from settings import settings

pool: asyncpg.Pool | None = None
logger: logging.Logger = logging.getLogger(__name__)


class Session:
    cursor_ctx: asyncpg.Pool | None = None

    def __init__(self, cursor_ctx):
        self.cursor_ctx = cursor_ctx

    async def fetch_rows(self, query: str, *args) -> list:
        try:
            async with self.cursor_ctx as cursor:
                if args:
                    data = await cursor.fetch(query, *args)
                else:
                    data = await cursor.fetch(query)

            return data
        except Exception as e:
            logger.error(f"exception '{e}' executing query: `{query}`")
            raise HTTPException(status_code=500, detail="internal error, try later")


async def setup_pool():
    global pool
    logger.debug(f"setting up db pool max={settings.database_pool_max_size} min={settings.database_pool_min_size}")
    pool = await asyncpg.create_pool(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
        max_size=settings.database_pool_max_size,
        min_size=settings.database_pool_min_size,
    )


async def close_pool():
    global pool
    logger.debug("closing db pool")
    await pool.close()


async def get_session() -> Session:
    global pool
    return Session(pool.acquire(timeout=settings.database_timeout))

