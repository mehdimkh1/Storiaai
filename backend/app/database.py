"""Database utilities."""
from __future__ import annotations

import contextlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings


def _create_engine():
    settings = get_settings()
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    return create_engine(settings.database_url, echo=settings.database_echo, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependencies."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create database tables."""

    from . import models  # noqa: F401  pylint: disable=unused-import

    Base.metadata.create_all(bind=engine)
