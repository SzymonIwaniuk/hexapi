from datetime import date, timedelta
from domain.batches import Batch, Orderline, allocate


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments() -> None:
    in_stock_batch = Batch("in-stock-batch", "AMPLIFIER", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "AMPLIFIER", 100, eta=tomorrow)
    line = Orderline("oref", "AMPLIFIER", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches() -> None:
    earliest = Batch("speedy-batch", "MINIMALIST-MICRO", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-MICRO", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-MICRO", 100, eta=later)
    line = Orderline("order1", "MINIMALIST-MICRO", 3)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 97
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100
