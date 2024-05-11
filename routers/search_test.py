from unittest import mock

import pytest
from fastapi.testclient import TestClient
from main import app
from dependencies.database import test_db
from repositories.events import EventsRepository, CreateEventData


@pytest.mark.parametrize("location,radius,response_code,include_first,include_second", [
    (None, None, 422, False, False),
    ('19.4248097,-99.1961895', None, 422, False, False),
    (None, 650.0, 422, False, False),
    ('not an coordinate', 650.0, 422, False, False),
    ('19.4248097,-99.1961895', 'not a radius', 422, False, False),
    ('19.4248097,-99.1961895', 1000000000, 422, False, False),
    ('19.4248097,-99.1961895', 50.0, 422, False, False),
    ('19.4295155,-99.1933465', 100.0, 200, False, False),
    ('19.4248097,-99.1961895', 100.0, 200, True, False),
    ('19.433949,-99.196737', 100.0, 200, False, True),
    ('19.4295155,-99.1933465', 1000.0, 200, True, True),
])
@pytest.mark.asyncio
async def test_search_nearby(location, radius, response_code, include_first, include_second, test_db):
    events_repo = EventsRepository(test_db)
    first_event = await events_repo.create_event(CreateEventData(
        id=None,
        location='19.4248097,-99.1961895',
        address='Av. P.º de la Reforma 50, Polanco V Secc, Miguel Hidalgo, 11580 Ciudad de México, CDMX',
        locale='es-MX',
        title='El sol regresa',
        description='Luis Miguel en vivo si sigue vivo',
        slug=None,
        tags=[],
        publisher_id=None,
        created_at=None,
        updated_at=None,
    ))
    second_event = await events_repo.create_event(CreateEventData(
        id=None,
        location='19.433949,-99.196737',
        address='Av. Horacio, Polanco, Polanco III Secc, Miguel Hidalgo, 11540 Ciudad de México, CDMX',
        locale='es-MX',
        title='Saludo al sol',
        description='Yoga feliz',
        slug=None,
        tags=[],
        publisher_id=None,
        created_at=None,
        updated_at=None,
    ))
    assert first_event is not None and second_event is not None

    def get_event_data(event):
        return {
            "id": str(event.id),
            "locale": event.locale,
            "location": event.location,
            "address": event.address,
            "title": event.title,
            "description": event.description,
            "slug": event.slug,
            "tags": event.tags,
            "publisher_id": event.publisher_id,
            "publisher_display_name": None,
            "publisher_display_image": None,
            "created_at": mock.ANY,
            "updated_at": mock.ANY,
        }

    try:
        with TestClient(app) as client:
            response = client.get('/search-nearby', params={
                'location': location,
                'radius': radius,
            })
            assert response.status_code == response_code, response.content
            if response_code != 200:
                return

            response_data = response.json()
            assert len(response_data) == int(include_first) + int(include_second)
            if include_first:
                assert get_event_data(first_event) in response_data

            if include_second:
                assert get_event_data(second_event) in response_data
    finally:
        await events_repo.delete_event_by_id(first_event.id)
        await events_repo.delete_event_by_id(second_event.id)
