import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from lite_catalog_demo.model import LotNotFound, LotStatus
from lite_catalog_demo.repository import SQLAlchemyRepository


def test_repository_can_get_lot(session: Session) -> None:
    test_rows = [
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

    session.execute(
        text(
            "INSERT INTO lots (number, price, rooms, status, client) VALUES"
            "(:number, :price, :rooms, :status, :client)"
        ),
        test_rows,
    )

    repo = SQLAlchemyRepository(session)
    received_lot = repo.get("103")

    assert received_lot.number == "103"
    assert received_lot.price == 14_000_000
    assert received_lot.rooms == 2
    assert received_lot.status == LotStatus.SOLD
    assert received_lot.client == "Artem Volkov"


def test_repository_raises_when_lot_not_found(session: Session) -> None:
    test_rows = [
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

    session.execute(
        text(
            "INSERT INTO lots (number, price, rooms, status, client) VALUES"
            "(:number, :price, :rooms, :status, :client)"
        ),
        test_rows,
    )

    repo = SQLAlchemyRepository(session)

    with pytest.raises(LotNotFound, match="999"):
        repo.get("999")
