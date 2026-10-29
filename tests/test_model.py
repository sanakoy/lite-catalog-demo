import pytest

from lite_catalog_demo.model import Lot, LotUnavailable


def test_booking_available_lot_marks_it_booked_for_client():
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book("Ivan Gromov")

    assert lot.status == "booked"
    assert lot.client == "Ivan Gromov"


def test_cannot_book_already_booked_lot():
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book("Ivan Gromov")

    with pytest.raises(LotUnavailable):
        lot.book("Artem Volkov")

    assert lot.status == "booked"
    assert lot.client == "Ivan Gromov"
