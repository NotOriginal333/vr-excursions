from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Excursion(Base):
    __tablename__ = "excursions"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]
    description: Mapped[str]
    content_type: Mapped[str]
    page_url: Mapped[str]
    media_url: Mapped[str]
    license: Mapped[str]
    license_url: Mapped[str | None]
    author: Mapped[str]
    subject: Mapped[str]
    grade: Mapped[int]
    topic: Mapped[str]
