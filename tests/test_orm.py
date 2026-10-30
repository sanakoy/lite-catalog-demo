from sqlalchemy import select, text
from sqlalchemy.orm import Session

from lite_catalog_demo.model import Lot, LotStatus
from lite_catalog_demo.orm import lots


def test_lot_mapper_can_load_lots(session: Session) -> None:
    expected_rows = [
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
        expected_rows,
    )

    received_lots = session.scalars(select(Lot).order_by(lots.c.number)).all()

    assert [
        {
            "number": lot.number,
            "price": lot.price,
            "rooms": lot.rooms,
            "status": lot.status,
            "client": lot.client,
        }
        for lot in received_lots
    ] == expected_rows

    for lot in received_lots:
        assert isinstance(lot.status, LotStatus)
