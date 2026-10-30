from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from lite_catalog_demo.orm import metadata, start_mappers


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()
