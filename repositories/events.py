import json
import uuid
from datetime import datetime, timezone
from typing import Annotated, List
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, Json, Field
from slugify import slugify
from html_sanitizer import Sanitizer

from dependencies.database import get_session, Session
from repositories import patterns


class Event(BaseModel):
    id: UUID
    location: str
    address: str = Field(max_length=2048)
    locale: str = Field(max_length=10, pattern=patterns.LOCALE_IETF)
    title: str = Field(max_length=50)
    description: str
    slug: str
    tags: Json[List[str]]
    publisher_id: UUID | None
    publisher_display_name: str | None
    publisher_display_image: str | None
    created_at: datetime
    updated_at: datetime


class CreateEventData(BaseModel):
    id: UUID | None
    location: str = Field(pattern=patterns.GPS_LAT_LNG)
    address: str = Field(max_length=2048)
    locale: str = Field(max_length=10, pattern=patterns.LOCALE_IETF)
    title: str = Field(max_length=50)
    description: str
    slug: str | None
    tags: List[str]
    publisher_id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None

    def sanitize(self):
        remove_html = Sanitizer({})

        if not self.id:
            self.id = uuid.uuid4()

        self.title = remove_html.sanitize(self.title)
        self.description = remove_html.sanitize(self.description)
        self.tags = [remove_html.sanitize(str(tag)) for tag in self.tags]

        if not self.slug:
            self.slug = slugify(remove_html.sanitize(self.title), max_length=100)

        if not self.created_at:
            self.created_at = datetime.now(tz=timezone.utc)

        if not self.updated_at:
            self.updated_at = self.created_at


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

    async def create_event(self, event: CreateEventData) -> Event:
        query = """
        WITH inserted_event AS (
            INSERT INTO events
                (id, location, 
                    address, locale, title, description, slug, tags, publisher_id, created_at, updated_at)
            VALUES
                ($1::uuid, st_point($2::float, $3::float, 4326)::geography, 
                    $4, $5, $6, $7, $8, $9::jsonb, $10::uuid, $11, $12)
            RETURNING *        
        ) SELECT 
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
        FROM inserted_event evt LEFT JOIN publishers pub ON (evt.publisher_id = pub.id);
        """
        event.sanitize()
        [loc_lat, loc_lng] = event.location.split(',') or [0.0, 0.0]
        tags_json = json.dumps(event.tags)

        row = await self.session.fetch_first(query, event.id, float(loc_lng), float(loc_lat), event.address,
                                             event.locale, event.title, event.description, event.slug, tags_json,
                                             event.publisher_id, event.created_at, event.updated_at)
        assert row is not None, "invalid result from query, this should not happen"
        return Event.model_validate(dict(row))

    async def delete_event_by_id(self, event_id: UUID) -> bool:
        query = """
        DELETE FROM events evt WHERE evt.id = $1;
        """
        status = await self.session.execute(query, str(event_id))
        return "delete 1" == status.lower()
