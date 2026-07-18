"""Database session management."""

from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.base import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    from app.database.base import Base
    from app.models import user, sale, payout, withdrawal, adjustment  # noqa: F401
    Base.metadata.create_all(bind=engine)
