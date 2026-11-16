"""Database engine and session helpers."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine


def make_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite:///"):
        db_path = Path(database_url.removeprefix("sqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(database_url, connect_args={"check_same_thread": False})
    return create_engine(database_url)


def init_db(engine: Engine) -> None:
    # Import models so their tables are registered on SQLModel.metadata.
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
