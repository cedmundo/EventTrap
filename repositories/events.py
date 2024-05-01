from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, ConfigDict, Json

from dependencies.database import get_session, Session


class Event(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID
    location: str
    address: str
    locale: str
    title: str
    description: str
    slug: str
    tags: Json[List[str]]
    publisher_id: UUID | None
    publisher_display_name: str | None
    publisher_display_image: str | None
    created_at: datetime
    updated_at: datetime


class EventsRepository:
    def __init__(self, session: Annotated[Session, Depends(get_session)]):
        self.session = session

    async def search_events(self, location: str, radius: float, skip: int, limit: int) -> [Event]:
        # TODO(cedmundo): Filter by next_date, also validate location, radius, skip and limit values
        query = """
        SELECT
            evt.id,
            CONCAT(st_y(evt.location::geometry), ',', st_x(evt.location::geometry)) AS location,
            evt.address,
            evt.locale,
            evt.title,
            evt.description,
            evt.slug,
            evt.tags,
            evt.publisher_id,
            pub.display_name AS publisher_display_name,
            pub.display_image AS publisher_display_image,
            evt.created_at,
            evt.updated_at
        FROM events evt
        LEFT JOIN publishers pub ON (evt.publisher_id = pub.id)
        WHERE st_distance(evt.location, st_point($1::float, $2::float, 4326)::geography) < $3::float
        LIMIT $4::int OFFSET $5::int;
        """
        [loc_lat, loc_lng] = location.split(',') or [0.0, 0.0]
        rows = await self.session.fetch_rows(query, float(loc_lng), float(loc_lat), radius, limit, skip)
        data = [Event.model_validate(dict(row)) for row in rows]
        return list(data)
