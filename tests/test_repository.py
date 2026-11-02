import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from lite_catalog_demo.model import Lot, LotNotFound, LotStatus
from lite_catalog_demo.repository import AbstractRepository, SQLAlchemyRepository


class FakeRepository(AbstractRepository):
    def __init__(self) -> None:
        self.lots: list[Lot] = []

    def get(self, number: str) -> Lot:
        for lot in self.lots:
            if lot.number == number:
                return lot
        raise LotNotFound(number=number)

    def add(self, lot: Lot) -> None:
        if lot in self.lots:
            raise ValueError(f"Лот с номером {lot.number} уже существует")
        self.lots.append(lot)

    def list_all(self) -> list[Lot]:
        return list(self.lots)


@pytest.fixture(params=["sqlalchemy", "fake"])
def repo(request: pytest.FixtureRequest) -> AbstractRepository:
    if request.param == "sqlalchemy":
        return SQLAlchemyRepository(request.getfixturevalue("session"))
    return FakeRepository()


def get_test_rows() -> list[dict[str, object]]:
    return [
        {
            "number": "101",
            "price": 17_000_000,
            "rooms": 3,
            "status": LotStatus.AVAILABLE,
            "client": None,
        },
        {
            "number": "102",
            "price": 14_000_000,
            "rooms": 2,
            "status": LotStatus.BOOKED,
            "client": "Ivan Gromov",
        },
        {
            "number": "103",
            "price": 14_000_000,
            "rooms": 2,
            "status": LotStatus.SOLD,
            "client": "Artem Volkov",
        },
    ]


def insert_lots(session: Session) -> None:
    test_rows = get_test_rows()

    session.execute(
        text(
            "INSERT INTO lots (number, price, rooms, status, client) VALUES"
            "(:number, :price, :rooms, :status, :client)"
        ),
        test_rows,
    )


def test_repository_can_get_lot(session: Session) -> None:
    insert_lots(session)

    repo = SQLAlchemyRepository(session)
    received_lot = repo.get("103")

    assert received_lot.number == "103"
    assert received_lot.price == 14_000_000
    assert received_lot.rooms == 2
    assert received_lot.status == LotStatus.SOLD
    assert received_lot.client == "Artem Volkov"


def test_repository_can_add_lot(session: Session) -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=14_000_000, rooms=2)
    lot_3 = Lot(number="103", price=14_000_000, rooms=2)
    lot_2.book("Ivan Gromov")
    lot_3.book("Artem Volkov")
    lot_3.sell("Artem Volkov")

    expected_lots = [lot_1, lot_2, lot_3]
    repo = SQLAlchemyRepository(session)
    for lot in expected_lots:
        repo.add(lot)
    session.commit()

    received_rows = session.execute(
        text("SELECT number, price, rooms, status, client FROM lots ORDER BY number")
    ).all()

    expected_rows = get_test_rows()
    assert [
        {
            "number": row.number,
            "price": row.price,
            "rooms": row.rooms,
            "status": row.status,
            "client": row.client,
        }
        for row in received_rows
    ] == expected_rows


def test_repository_add_does_not_commit(session: Session) -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)

    repo = SQLAlchemyRepository(session)
    repo.add(lot)
    session.rollback()

    received_rows = session.execute(
        text("SELECT number, price, rooms, status, client FROM lots")
    ).all()

    assert len(received_rows) == 0


def test_repository_list_all_lots(session: Session) -> None:
    insert_lots(session)

    repo = SQLAlchemyRepository(session)
    received_lots = repo.list_all()

    expected_rows = get_test_rows()
    sorted_received_lots = sorted(received_lots, key=lambda lot: lot.number)
    assert [
        {
            "number": lot.number,
            "price": lot.price,
            "rooms": lot.rooms,
            "status": lot.status,
            "client": lot.client,
        }
        for lot in sorted_received_lots
    ] == expected_rows

    for lot in received_lots:
        assert isinstance(lot, Lot)


def test_repository_lists_added_lot(repo: AbstractRepository) -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=14_000_000, rooms=2)
    lot_3 = Lot(number="103", price=14_000_000, rooms=2)

    expected_lots = [lot_1, lot_2, lot_3]

    for lot in expected_lots:
        repo.add(lot)

    received_lots = repo.list_all()
    sorted_lots = sorted(received_lots, key=lambda lot: lot.number)

    assert expected_lots == sorted_lots


def test_repository_get_added_lot(repo: AbstractRepository) -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=14_000_000, rooms=2)
    lot_3 = Lot(number="103", price=14_000_000, rooms=2)

    expected_lots = [lot_1, lot_2, lot_3]

    for lot in expected_lots:
        repo.add(lot)

    received_lot_1 = repo.get("101")
    received_lot_2 = repo.get("102")
    received_lot_3 = repo.get("103")

    assert received_lot_1 is lot_1
    assert received_lot_2 is lot_2
    assert received_lot_3 is lot_3


def test_repository_get_raises_not_found(repo: AbstractRepository) -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    repo.add(lot)

    with pytest.raises(LotNotFound, match="999"):
        repo.get("999")
