from typing import Protocol

from lite_catalog_demo.model import book_cheapest
from lite_catalog_demo.repository import AbstractRepository


class Committable(Protocol):
    def commit(self) -> None:
        pass


def book_cheapest_lot(
    repo: AbstractRepository,
    session: Committable,
    max_price: int,
    rooms: int,
    client: str,
) -> str:
    lots = repo.list_all()
    number = book_cheapest(lots=lots, max_price=max_price, rooms=rooms, client=client)
    session.commit()
    return number
