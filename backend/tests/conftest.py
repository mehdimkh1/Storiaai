"""Pytest fixtures."""
from __future__ import annotations

import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app import database as database_module
from app.config import get_settings

_TEMP_DB = tempfile.NamedTemporaryFile(prefix="storiaai-test", suffix=".db", delete=False)
_TEMP_DB.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEMP_DB.name}"
os.environ["OFFLINE_MODE"] = "true"
get_settings.cache_clear()  # type: ignore[attr-defined]

from app.database import Base, SessionLocal, engine, get_db, _create_engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _cleanup_env() -> Generator[None, None, None]:
    """Cleanup temporary database after tests."""

    try:
        yield
    finally:
        try:
            SessionLocal.close_all_sessions()
        except Exception:  # pragma: no cover
            pass
        try:
            database_module.engine.dispose()
        except Exception:  # pragma: no cover
            pass
        try:
            os.remove(_TEMP_DB.name)
        except (FileNotFoundError, PermissionError):
            pass


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return API client with isolated database."""

    engine.dispose()
    new_engine = _create_engine()
    Base.metadata.bind = new_engine
    database_module.engine = new_engine

    SessionLocal.configure(bind=new_engine)

    Base.metadata.drop_all(bind=new_engine)
    Base.metadata.create_all(bind=new_engine)

    def _override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
