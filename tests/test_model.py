import pytest

from lite_catalog_demo.model import (
    BookingNotFound,
    Lot,
    LotStatus,
    LotUnavailable,
    NoSuitableLot,
    book_cheapest,
)

IVAN = "Ivan Gromov"
ARTEM = "Artem Volkov"
ANNA = "Anna Zaytseva"


def test_booking_available_lot_marks_it_booked() -> None:
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book(IVAN)

    assert lot.status == LotStatus.BOOKED
    assert lot.client == IVAN


def test_cannot_book_already_booked_lot() -> None:
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book(IVAN)

    with pytest.raises(LotUnavailable):
        lot.book(ARTEM)

    assert lot.status == LotStatus.BOOKED
    assert lot.client == IVAN


def test_cannot_book_already_sold_lot() -> None:
    lot = Lot(number="101", price=12_000_000, rooms=2)
    lot.book(ARTEM)
    lot.sell(ARTEM)

    with pytest.raises(LotUnavailable):
        lot.book(ARTEM)

    assert lot.status == LotStatus.SOLD
    assert lot.client == ARTEM


def test_cancel_booking_for_booked_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(ANNA)
    lot.cancel_booking(ANNA)

    assert lot.status == LotStatus.AVAILABLE
    assert lot.client is None


def test_cannot_cancel_booking_of_available_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.cancel_booking(ANNA)

    assert exc_info.value.client == ANNA
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.AVAILABLE
    assert lot.client is None


def test_cannot_cancel_someone_elses_booking() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(ANNA)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.cancel_booking(IVAN)

    assert exc_info.value.client == IVAN
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.BOOKED
    assert lot.client == ANNA


def test_cannot_cancel_sold_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(IVAN)
    lot.sell(IVAN)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.cancel_booking(IVAN)

    assert exc_info.value.client == IVAN
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.SOLD
    assert lot.client == IVAN


def test_sell_booked_lot_marks_it_sold() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(IVAN)
    lot.sell(IVAN)

    assert lot.status == LotStatus.SOLD
    assert lot.client == IVAN


def test_cannot_sell_available_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.sell(IVAN)

    assert exc_info.value.client == IVAN
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.AVAILABLE
    assert lot.client is None


def test_cannot_sell_someone_elses_booking() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(ANNA)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.sell(IVAN)

    assert exc_info.value.client == IVAN
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.BOOKED
    assert lot.client == ANNA


def test_cannot_sell_someone_elses_sold_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(ANNA)
    lot.sell(ANNA)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.sell(IVAN)

    assert exc_info.value.client == IVAN
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.SOLD
    assert lot.client == ANNA


def test_cannot_sell_sold_lot() -> None:
    lot = Lot(number="101", price=17_000_000, rooms=3)
    lot.book(IVAN)
    lot.sell(IVAN)

    with pytest.raises(BookingNotFound) as exc_info:
        lot.sell(IVAN)

    assert exc_info.value.client == IVAN
    assert exc_info.value.number == "101"

    assert lot.status == LotStatus.SOLD
    assert lot.client == IVAN


def test_lots_with_same_number_are_equal() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="101", price=15_000_000, rooms=3)

    assert lot_1 == lot_2


def test_lots_with_different_number_are_not_equal() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=17_000_000, rooms=3)

    assert lot_1 != lot_2


def test_set_keeps_one_lot_per_number() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="101", price=15_000_000, rooms=3)

    lots = {lot_1, lot_2}

    assert len(lots) == 1


def test_lot_is_not_equal_to_its_number() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)

    assert lot_1 != lot_1.number


def test_book_cheapest_books_cheapest_matching_lot() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=15_000_000, rooms=3)
    lot_3 = Lot(number="103", price=15_500_000, rooms=3)
    lot_4 = Lot(number="104", price=14_000_000, rooms=2)

    lots = [lot_1, lot_2, lot_3, lot_4]
    number = book_cheapest(lots=lots, max_price=16_000_000, rooms=3, client=IVAN)

    assert number == lot_2.number
    assert lot_2.status == LotStatus.BOOKED
    assert lot_2.client == IVAN

    assert lot_1.status == LotStatus.AVAILABLE
    assert lot_3.status == LotStatus.AVAILABLE
    assert lot_4.status == LotStatus.AVAILABLE


def test_book_cheapest_skips_unavailable_lots() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=15_000_000, rooms=3)
    lot_3 = Lot(number="103", price=15_500_000, rooms=3)
    lot_4 = Lot(number="104", price=14_000_000, rooms=2)
    lot_5 = Lot(number="105", price=15_300_000, rooms=3)

    lot_2.book(ARTEM)
    lot_5.book(ANNA)
    lot_5.sell(ANNA)

    lots = [lot_1, lot_2, lot_3, lot_4, lot_5]
    number = book_cheapest(lots=lots, max_price=16_000_000, rooms=3, client=IVAN)

    assert number == lot_3.number
    assert lot_3.status == LotStatus.BOOKED
    assert lot_3.client == IVAN

    assert lot_1.status == LotStatus.AVAILABLE
    assert lot_2.status == LotStatus.BOOKED
    assert lot_4.status == LotStatus.AVAILABLE
    assert lot_5.status == LotStatus.SOLD


def test_book_cheapest_accepts_lot_priced_exactly_at_budget() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=16_000_000, rooms=3)

    number = book_cheapest(
        lots=[lot_1, lot_2], max_price=16_000_000, rooms=3, client=IVAN
    )

    assert number == lot_2.number
    assert lot_2.status == LotStatus.BOOKED
    assert lot_2.client == IVAN

    assert lot_1.status == LotStatus.AVAILABLE


def test_book_cheapest_raises_when_no_lot_matches() -> None:
    lot_1 = Lot(number="101", price=17_000_000, rooms=3)
    lot_2 = Lot(number="102", price=16_000_000, rooms=3)

    budget = 15_999_999
    with pytest.raises(NoSuitableLot) as exc_info:
        book_cheapest(lots=[lot_1, lot_2], max_price=budget, rooms=3, client=IVAN)

    assert exc_info.value.max_price == budget
    assert exc_info.value.rooms == 3
    assert exc_info.value.client == IVAN

    assert lot_1.status == LotStatus.AVAILABLE
    assert lot_2.status == LotStatus.AVAILABLE
