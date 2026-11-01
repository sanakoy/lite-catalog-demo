from enum import StrEnum


class LotUnavailable(Exception):
    pass


class BookingNotFound(Exception):
    def __init__(self, client: str, number: str) -> None:
        super().__init__(f"У клиента {client} не найдена бронь на лот {number}")
        self.client = client
        self.number = number


class NoSuitableLot(Exception):
    def __init__(self, client: str, max_price: int, rooms: int) -> None:
        super().__init__(
            f"Не нашелся свободный лот для клиента {client} с максимальной ценой {max_price} и комнатностью {rooms}"
        )
        self.client = client
        self.max_price = max_price
        self.rooms = rooms


class LotNotFound(Exception):
    def __init__(self, number: str) -> None:
        super().__init__(f"Лот с номером {number} не найден")
        self.number = number


class LotStatus(StrEnum):
    BOOKED = "booked"
    AVAILABLE = "available"
    SOLD = "sold"


class Lot:
    def __init__(self, number: str, price: int, rooms: int) -> None:
        self.number = number
        self.price = price
        self.rooms = rooms
        self.client: str | None = None
        self.status: LotStatus = LotStatus.AVAILABLE

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Lot):
            return NotImplemented

        return other.number == self.number

    def __hash__(self) -> int:
        return hash(self.number)

    def book(self, client: str) -> None:
        if not self.can_be_booked():
            raise LotUnavailable(f"Лот {self.number} недоступен")

        self.status = LotStatus.BOOKED
        self.client = client

    def cancel_booking(self, client: str) -> None:
        if not self._is_booked_by(client):
            raise BookingNotFound(client=client, number=self.number)

        self.status = LotStatus.AVAILABLE
        self.client = None

    def sell(self, client: str) -> None:
        if not self._is_booked_by(client):
            raise BookingNotFound(client=client, number=self.number)

        self.status = LotStatus.SOLD

    def can_be_booked(self) -> bool:
        return self.status == LotStatus.AVAILABLE

    def _is_booked_by(self, client: str) -> bool:
        return self.status == LotStatus.BOOKED and client == self.client


def book_cheapest(lots: list[Lot], max_price: int, rooms: int, client: str) -> str:
    suitable_lots = [
        lot
        for lot in lots
        if lot.price <= max_price and lot.rooms == rooms and lot.can_be_booked()
    ]
    if not suitable_lots:
        raise NoSuitableLot(client=client, max_price=max_price, rooms=rooms)

    cheapest_lot = min(suitable_lots, key=lambda lot: lot.price)
    cheapest_lot.book(client)
    return cheapest_lot.number
