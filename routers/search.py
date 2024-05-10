from typing import Annotated

from fastapi import APIRouter, Depends, Query

from repositories.events import EventsRepository

router = APIRouter()
coordinate_regex = r'^((\-?|\+?)?\d+(\.\d+)?),\s*((\-?|\+?)?\d+(\.\d+)?)$'


class SearchQueryParams:
    def __init__(
            self,
            location: Annotated[str, Query(pattern=coordinate_regex, description="standard lat,long coordinate")],
            radius: Annotated[float, Query(ge=100.0, lt=10000.0, description="radius in meters")],
            skip: Annotated[int, Query(ge=0, description="result skip for pagination")] = 0,
            limit: Annotated[int, Query(ge=10, lt=100, description="amount of results per page")] = 50,
    ):
        self.location = location
        self.radius = radius
        self.skip = skip
        self.limit = limit


@router.get("/search-nearby", tags=["events"], description="Search events in geographic area")
async def search_nearby(events: Annotated[EventsRepository, Depends()],
                        params: Annotated[SearchQueryParams, Depends()]):
    return await events.search_events(params.location, params.radius, params.skip, params.limit)
