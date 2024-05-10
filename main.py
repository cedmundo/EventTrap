from contextlib import asynccontextmanager

from fastapi import FastAPI

from dependencies import database
from routers import search


@asynccontextmanager
async def lifespan(setup_app: FastAPI):
    await database.setup_pool(setup_app)
    yield
    await database.close_pool(setup_app)


app = FastAPI(lifespan=lifespan)
app.include_router(search.router)
