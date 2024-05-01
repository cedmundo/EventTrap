from contextlib import asynccontextmanager

from fastapi import FastAPI

from dependencies import database
from routers import search


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await database.setup_pool()
    yield
    await database.close_pool()


app = FastAPI(lifespan=lifespan)
app.include_router(search.router)
