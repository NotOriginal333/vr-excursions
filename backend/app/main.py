import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from valkey.asyncio import Valkey

from app import catalog
from app.cache import cached
from app.models import Base, Excursion
from app.schemas import ExcursionOut, Filters, Page, PgInt, Topic


def create_app(database_url: str, cache_client, seed_path: Path, cache_ttl_seconds: int) -> FastAPI:
    engine = create_async_engine(database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        await catalog.load_seed(sessions, seed_path)
        yield
        await engine.dispose()

    async def open_session():
        async with sessions() as session:
            yield session

    DbSession = Annotated[AsyncSession, Depends(open_session)]
    app = FastAPI(title="VR Excursions API", lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")
    Instrumentator(registry=CollectorRegistry()).instrument(app).expose(app)

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/excursions", response_model=Page)
    async def search(filters: Annotated[Filters, Query()], session: DbSession):
        async def page_as_json():
            return (await catalog.search(session, filters)).model_dump(mode="json")

        return await cached(cache_client, f"excursions:{filters.model_dump_json()}", cache_ttl_seconds, page_as_json)

    @app.get("/api/excursions/{excursion_id}")
    async def card(excursion_id: PgInt, session: DbSession) -> ExcursionOut:
        if excursion := await session.get(Excursion, excursion_id):
            return ExcursionOut.model_validate(excursion)
        raise HTTPException(status_code=404, detail="Excursion not found")

    @app.get("/api/topics")
    async def topics(session: DbSession) -> list[Topic]:
        return await catalog.topics(session)

    return app


def from_env() -> FastAPI:
    return create_app(
        os.environ["DATABASE_URL"],
        Valkey.from_url(os.environ["VALKEY_URL"]),
        Path("data/excursions.json"),
        cache_ttl_seconds=60,
    )
