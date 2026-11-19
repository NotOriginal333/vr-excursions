from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

PG_INT_MAX = 2**31 - 1
PgInt = Annotated[int, Field(ge=-PG_INT_MAX - 1, le=PG_INT_MAX)]


class ExcursionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    content_type: str
    page_url: str
    media_url: str
    license: str
    license_url: str | None
    author: str
    subject: str
    grade: int
    topic: str


class Filters(BaseModel):
    q: str | None = None
    subject: str | None = None
    grade: PgInt | None = None
    topic: str | None = None
    content_type: str | None = None
    page: int = Field(1, ge=1, le=PG_INT_MAX)
    size: int = Field(20, ge=1, le=100)

    @field_validator("q", "subject", "grade", "topic", "content_type", mode="before")
    @classmethod
    def blank_means_any(cls, value):
        return value or None


class Page(BaseModel):
    items: list[ExcursionOut]
    total: int
    page: int
    size: int


class Topic(BaseModel):
    subject: str
    grade: int
    topic: str
