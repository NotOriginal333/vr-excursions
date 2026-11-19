import asyncio
import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.main import create_app
from app.models import Base


class FakeCache:
    def __init__(self):
        self.store = {}
        self.writes = []

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex):
        self.store[key] = value
        self.writes.append((key, ex))


def excursion(title: str, **fields) -> dict:
    return {
        "external_id": title,
        "title": title,
        "description": "",
        "content_type": "360_photo",
        "page_url": f"https://commons.wikimedia.org/wiki/File:{title}.jpg",
        "media_url": f"https://upload.wikimedia.org/{title}.jpg",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "author": "Author",
        "subject": "Географія",
        "grade": 6,
        "topic": "Вулкани",
        **fields,
    }


@pytest.fixture(scope="session")
def database_url():
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
    from testcontainers.community.postgres import PostgresContainer

    with PostgresContainer("postgres:17", driver="asyncpg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
def cache():
    return FakeCache()


@pytest.fixture
def make_client(database_url, cache, tmp_path):
    def make(*records, cache_ttl_seconds=60):
        seed = tmp_path / "excursions.json"
        seed.write_text(json.dumps(records), encoding="utf-8")
        return TestClient(create_app(database_url, cache, seed, cache_ttl_seconds))

    yield make
    asyncio.run(drop_tables(database_url))


async def drop_tables(database_url):
    engine = create_async_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()
