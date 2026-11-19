import json
import re
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Excursion
from app.schemas import ExcursionOut, Filters, Page, Topic

EXACT_FILTERS = ("subject", "grade", "topic", "content_type")
SEARCHABLE_TEXT = func.concat_ws(" ", Excursion.title, Excursion.description, Excursion.topic)


def prefix_query(text: str) -> str:
    return " & ".join(f"{word}:*" for word in re.findall(r"\w+", text))


def conditions(filters: Filters) -> list:
    matched = [
        getattr(Excursion, name) == value for name in EXACT_FILTERS if (value := getattr(filters, name)) is not None
    ]
    if filters.q and (query := prefix_query(filters.q)):
        matched.append(func.to_tsvector("simple", SEARCHABLE_TEXT).bool_op("@@")(func.to_tsquery("simple", query)))
    return matched


async def search(session: AsyncSession, filters: Filters) -> Page:
    where = conditions(filters)
    total = await session.scalar(select(func.count()).select_from(Excursion).where(*where))
    rows = await session.scalars(
        select(Excursion)
        .where(*where)
        .order_by(Excursion.id)
        .offset((filters.page - 1) * filters.size)
        .limit(filters.size)
    )
    return Page(
        items=[ExcursionOut.model_validate(row) for row in rows], total=total, page=filters.page, size=filters.size
    )


async def topics(session: AsyncSession) -> list[Topic]:
    rows = await session.execute(
        select(Excursion.subject, Excursion.grade, Excursion.topic)
        .distinct()
        .order_by(Excursion.subject, Excursion.grade, Excursion.topic)
    )
    return [Topic(subject=subject, grade=grade, topic=topic) for subject, grade, topic in rows]


async def load_seed(sessions: async_sessionmaker, path: Path) -> None:
    async with sessions() as session:
        if await session.scalar(select(func.count()).select_from(Excursion)):
            return
        session.add_all(Excursion(**record) for record in json.loads(path.read_text(encoding="utf-8")))
        await session.commit()
