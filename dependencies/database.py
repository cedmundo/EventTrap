import asyncio
import logging
import uuid
from typing import AsyncGenerator

import asyncpg
import pytest_asyncio
from fastapi import HTTPException, FastAPI, Request

from settings import settings

logger: logging.Logger = logging.getLogger(__name__)


class Session:
    def __init__(self, pool):
        self.pool = pool
        self.connection = None
        self.connection_id = None

    async def setup_testing_connection(self, connection_id=None):
        self.connection = await self.pool.acquire(timeout=settings.database_timeout)
        # self.connection_id = str(uuid.uuid4()) if connection_id is None else connection_id
        # await self.connection.execute("PREPARE TRANSACTION '%s'" % self.connection_id)

    async def close_testing_connection(self):
        # await self.connection.execute("ROLLBACK PREPARED '%s'" % self.connection_id)
        if self.connection:
            await self.pool.release(self.connection)

    async def fetch_rows(self, query: str, *args) -> list:
        try:
            if self.connection is not None:
                return await self.connection.fetch(query, *args)

            async with self.pool.acquire(timeout=settings.database_timeout) as cursor:
                return await cursor.fetch(query, *args)
        except Exception as e:
            logger.error(f"exception '{e}' executing query: `{query}`")
            raise HTTPException(status_code=500, detail="internal error, try later")

    async def execute(self, query: str, *args) -> str:
        try:
            if self.connection is not None:
                return await self.connection.execute(query, *args)

            async with self.pool.acquire(timeout=settings.database_timeout) as cursor:
                return await cursor.execute(query, *args)
        except Exception as e:
            logger.error(f"exception '{e}' executing query: `{query}`")
            raise HTTPException(status_code=500, detail="internal error, try later")

    async def fetch_first(self, query: str, *args) -> asyncpg.Record:
        rows = await self.fetch_rows(query, *args)
        return rows[0] if len(rows) > 0 else None


async def get_connection_pool(loop=None, force_size=None) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
        max_size=settings.database_pool_max_size if force_size is None else force_size,
        min_size=settings.database_pool_min_size if force_size is None else force_size,
        loop=loop,
    )


async def setup_pool(app: FastAPI):
    logger.debug(f"setting up db pool max={settings.database_pool_max_size} min={settings.database_pool_min_size}")
    app.state.pool = await get_connection_pool()


async def close_pool(app: FastAPI):
    logger.debug("closing db pool")
    await app.state.pool.close()


async def get_session(request: Request) -> Session:
    return Session(request.app.state.pool)


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[Session, None]:
    pool = await get_connection_pool(loop=asyncio.get_running_loop(), force_size=1)
    session = Session(pool)
    await session.setup_testing_connection()
    yield session
    await session.close_testing_connection()
    await pool.close()
