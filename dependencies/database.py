import logging

import asyncpg
from fastapi import HTTPException, FastAPI, Request

from settings import settings

logger: logging.Logger = logging.getLogger(__name__)


class Session:
    def __init__(self, pool):
        self.pool = pool

    async def fetch_rows(self, query: str, *args) -> list:
        try:
            async with self.pool.acquire(timeout=settings.database_timeout) as cursor:
                if args:
                    data = await cursor.fetch(query, *args)
                else:
                    data = await cursor.fetch(query)

            return data
        except Exception as e:
            logger.error(f"exception '{e}' executing query: `{query}`")
            raise HTTPException(status_code=500, detail="internal error, try later")

    async def fetch_first(self, query: str, *args) -> asyncpg.Record:
        rows = await self.fetch_rows(query, *args)
        return rows[0] if len(rows) > 0 else None

    async def execute(self, query: str, *args) -> str:
        try:
            async with self.pool.acquire(timeout=settings.database_timeout) as cursor:
                if args:
                    status = await cursor.execute(query, *args)
                else:
                    status = await cursor.execute(query)
                return status
        except Exception as e:
            logger.error(f"exception '{e}' executing query: `{query}`")
            raise HTTPException(status_code=500, detail="internal error, try later")


async def get_connection_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
        max_size=settings.database_pool_max_size,
        min_size=settings.database_pool_min_size,
    )


async def setup_pool(app: FastAPI):
    logger.debug(f"setting up db pool max={settings.database_pool_max_size} min={settings.database_pool_min_size}")
    app.state.pool = await get_connection_pool()


async def close_pool(app: FastAPI):
    logger.debug("closing db pool")
    await app.state.pool.close()


async def get_session(request: Request) -> Session:
    return Session(request.app.state.pool)
