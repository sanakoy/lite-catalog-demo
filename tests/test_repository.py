import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from lite_catalog_demo.model import Lot, LotNotFound, LotStatus
from lite_catalog_demo.repository import SQLAlchemyRepository


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


def test_repository_raises_when_lot_not_found(session: Session) -> None:
    insert_lots(session)

    repo = SQLAlchemyRepository(session)
    with pytest.raises(LotNotFound, match="999"):
        repo.get("999")


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
