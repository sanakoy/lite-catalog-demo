from lite_catalog_demo.model import Lot, LotNotFound
from lite_catalog_demo.repository import AbstractRepository


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


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True
