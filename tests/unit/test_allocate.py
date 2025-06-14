from datetime import date, timedelta

import pytest

from domain.events import OutOfStock
from domain.model import Batch, OrderLine
from domain.services import allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments() -> None:
    in_stock_batch = Batch("in-stock-batch", "AMPLIFIER", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "AMPLIFIER", 100, eta=tomorrow)
    line = OrderLine("oref", "AMPLIFIER", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches() -> None:
    earliest = Batch("speedy-batch", "MINIMALIST-MICRO", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-MICRO", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-MICRO", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-MICRO", 3)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 97
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_raises_out_of_stock_exception_if_cannot_allocate() -> None:
    batch = Batch("batch1", "SMALL-AMPLIFIER", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-AMPLIFIER", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-AMPLIFIER"):
        allocate(OrderLine("order2", "SMALL-AMPLIFIER", 1), [batch])


def test_returns_allocated_batch_ref() -> None:
    in_stock_batch = Batch("in-stock-batch", "BIG-SPEAKER", 10, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "BIG-SPEAKER", 10, eta=tomorrow)
    line = OrderLine("oref", "BIG-SPEAKER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference
