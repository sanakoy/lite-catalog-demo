from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from lite_catalog_demo.orm import metadata, start_mappers
from lite_catalog_demo.repository import AbstractRepository, SQLAlchemyRepository
from tests.fakes import FakeRepository


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()


@pytest.fixture(params=["sqlalchemy", "fake"])
def repo(request: pytest.FixtureRequest) -> AbstractRepository:
    if request.param == "sqlalchemy":
        return SQLAlchemyRepository(request.getfixturevalue("session"))
    return FakeRepository()


@pytest.fixture
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    engine = create_engine(f"sqlite:///{tmp_path / 'lots.db'}")
    metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(bind=engine)
    clear_mappers()
    engine.dispose()
