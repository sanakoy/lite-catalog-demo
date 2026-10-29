class LotUnavailable(Exception):
    pass


class Lot:
    def __init__(self, number: str, price: int, rooms: int):
        self.number = number
        self.price = price
        self.rooms = rooms
        self.client = None
        self.status = "available"

    def book(self, client: str):
        if self.status != "available":
            raise LotUnavailable(f"Лот {self.number} недоступен")

        self.status = "booked"
        self.client = client
