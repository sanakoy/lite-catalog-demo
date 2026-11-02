import pytest
from sqlalchemy.orm import Session, sessionmaker

from lite_catalog_demo.model import Lot, LotStatus, NoSuitableLot
from lite_catalog_demo.repository import AbstractRepository, SQLAlchemyRepository
from lite_catalog_demo.service import book_cheapest_lot
from tests.fakes import FakeRepository, FakeSession


def test_book_cheapest_lot_books_and_commits() -> None:
    lot = Lot(number="102", price=15_000_000, rooms=3)

    repo: AbstractRepository = FakeRepository()
    fake_session = FakeSession()

    repo.add(lot)

    number = book_cheapest_lot(
        repo=repo,
        session=fake_session,
        max_price=16_000_000,
        rooms=3,
        client="Ivan Gromov",
    )

    assert fake_session.committed is True
    assert number == "102"
    assert lot.status == LotStatus.BOOKED
    assert lot.client == "Ivan Gromov"


def test_book_cheapest_lot_doesnt_commit_when_not_suitable_lot() -> None:
    lot = Lot(number="102", price=15_000_000, rooms=3)

    repo: AbstractRepository = FakeRepository()
    fake_session = FakeSession()

    repo.add(lot)

    with pytest.raises(NoSuitableLot):
        book_cheapest_lot(
            repo=repo,
            session=fake_session,
            max_price=14_999_999,
            rooms=3,
            client="Ivan Gromov",
        )

    assert fake_session.committed is False
    assert lot.status == LotStatus.AVAILABLE
    assert lot.client is None


def test_booking_survives_new_session(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as first:
        repo = SQLAlchemyRepository(first)
        repo.add(Lot(number="101", price=17_000_000, rooms=3))
        first.commit()

    with session_factory() as second:
        repo = SQLAlchemyRepository(second)
        book_cheapest_lot(
            repo=repo,
            session=second,
            max_price=18_000_000,
            rooms=3,
            client="Ivan Gromov",
        )

    with session_factory() as third:
        repo = SQLAlchemyRepository(third)
        lot = repo.get("101")
        assert lot.status == LotStatus.BOOKED
        assert lot.client == "Ivan Gromov"
