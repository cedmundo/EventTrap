from unittest import IsolatedAsyncioTestCase
from fastapi.testclient import TestClient

from dependencies.database import get_connection_pool, Session
from repositories.events import EventsRepository, CreateEventData, Event
from main import app

client = TestClient(app)


class Test(IsolatedAsyncioTestCase):
    first_event: Event

    async def asyncSetUp(self):
        self.pool = await get_connection_pool()
        self.event_repo = EventsRepository(Session(self.pool))
        self.first_event = await self.event_repo.create_event(CreateEventData(
            id=None,
            location='19.428909,-99.1692604',
            address='El Ángel de la Independencia',
            locale='es-MX',
            title='Porra de la selección',
            description='Celebramos que la selección mexicana ganó el mundial',
            tags=['celebracion', 'libre'],
            slug=None,
            publisher_id=None,
            created_at=None,
            updated_at=None,
        ))

    async def asyncTearDown(self):
        assert await self.event_repo.delete_event_by_id(self.first_event.id), "could not delete first_event"
        await self.pool.close()

    async def test_search_nearby(self):
        pass
