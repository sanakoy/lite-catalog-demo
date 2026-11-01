from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from lite_catalog_demo.model import Lot, LotNotFound


class AbstractRepository(ABC):
    @abstractmethod
    def get(self, number: str) -> Lot:
        raise NotImplementedError

    @abstractmethod
    def add(self, lot: Lot) -> None:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, number: str) -> Lot:
        query = select(Lot).filter_by(number=number)
        lot = self.session.scalars(query).one_or_none()
        if lot is None:
            raise LotNotFound(number=number)
        return lot

    def add(self, lot: Lot) -> None:
        self.session.add(lot)
