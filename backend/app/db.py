from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


class Base(DeclarativeBase):
    pass


if settings.database_url.startswith("sqlite"):
    # SQLite is only for local runs and the test suite. A single shared connection
    # is needed for in-memory databases (each connection would otherwise get its own).
    in_memory = settings.database_url.split("://", 1)[1] in ("", "/:memory:") or ":memory:" in settings.database_url
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        **({"poolclass": StaticPool} if in_memory else {}),
    )
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
