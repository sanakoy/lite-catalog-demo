import pytest

from lite_catalog_demo.model import BookingNotFound, Lot, LotStatus, LotUnavailable


def test_booking_available_lot_marks_it_booked() -> None:
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book("Ivan Gromov")

    assert lot.status == LotStatus.BOOKED
    assert lot.client == "Ivan Gromov"


def test_cannot_book_already_booked_lot() -> None:
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book("Ivan Gromov")

    with pytest.raises(LotUnavailable):
        lot.book("Artem Volkov")

    assert lot.status == LotStatus.BOOKED
    assert lot.client == "Ivan Gromov"


def test_cancel_booking_for_booked_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book("Anna Zaytseva")
    lot.cancel_booking("Anna Zaytseva")

    assert lot.status == LotStatus.AVAILABLE
    assert lot.client is None


def test_cannot_cancel_booking_of_available_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.cancel_booking("Anna Zaytseva")

    assert exc_info.value.client == "Anna Zaytseva"
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.AVAILABLE
    assert lot.client is None


def test_cannot_cancel_someone_elses_booking() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book("Anna Zaytseva")

    with pytest.raises(BookingNotFound) as exc_info:
        lot.cancel_booking("Ivan Gromov")

    assert exc_info.value.client == "Ivan Gromov"
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.BOOKED
    assert lot.client == "Anna Zaytseva"
