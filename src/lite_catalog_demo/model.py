from enum import StrEnum


class LotUnavailable(Exception):
    pass


class BookingNotFound(Exception):
    def __init__(self, client: str, number: str) -> None:
        super().__init__(f"У клиента {client} не найдена бронь на лот {number}")
        self.client = client
        self.number = number


class LotStatus(StrEnum):
    BOOKED = "booked"
    AVAILABLE = "available"


class Lot:
    def __init__(self, number: str, price: int, rooms: int) -> None:
        self.number = number
        self.price = price
        self.rooms = rooms
        self.client: str | None = None
        self.status: LotStatus = LotStatus.AVAILABLE

    def book(self, client: str) -> None:
        if self.status != LotStatus.AVAILABLE:
            raise LotUnavailable(f"Лот {self.number} недоступен")

        self.status = LotStatus.BOOKED
        self.client = client

    def cancel_booking(self, client: str) -> None:
        if self.status != LotStatus.BOOKED or client != self.client:
            raise BookingNotFound(client=client, number=self.number)

        self.status = LotStatus.AVAILABLE
        self.client = None
