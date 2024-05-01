from typing import Annotated

from fastapi import APIRouter, Depends

from repositories.events import EventsRepository

router = APIRouter()


@router.get("/search")
async def search(events: Annotated[EventsRepository, Depends(EventsRepository)],
                 location: str, radius: float, skip: int = 0, limit: int = 100):
    return await events.search_events(location, radius, skip, limit)

