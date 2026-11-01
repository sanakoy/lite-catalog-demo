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


def test_lot_mapper_can_save_lots(session: Session) -> None:
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

    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=14_000_000, rooms=2)
    lot_3 = Lot(number="103", price=14_000_000, rooms=2)
    lot_2.book("Ivan Gromov")
    lot_3.book("Artem Volkov")
    lot_3.sell("Artem Volkov")
    saved_lots = [lot_1, lot_2, lot_3]

    session.add_all(saved_lots)
    session.commit()

    received_rows = session.execute(
        text("SELECT number, price, rooms, status, client FROM lots ORDER BY number")
    ).all()

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
