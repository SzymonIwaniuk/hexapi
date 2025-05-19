from domain.batches import Batch, Orderline
from datetime import date
from typing import Tuple


# helper function
def make_batch_and_line(
        sku: str,
        batch_qty: int,
        line_qty: int
) -> Tuple[Batch, Orderline]:

    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        Orderline('order-123', sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_available_quantity() -> None:
    batch = Batch("batch-001", "SONY-HEADPHONES", qty=20, eta=date.today())
    line = Orderline("order-ref", "SONY-HEADPHONES", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_grater_than_required() -> None:
    large_batch, small_line = make_batch_and_line("JBL-HEADPHONES", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_grater_than_required() -> None:
    small_batch, large_line = make_batch_and_line("MICROPHONE", 3, 15)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required() -> None:
    batch, line = make_batch_and_line("SONY-LINKBUDS", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match() -> None:
    batch = Batch("batch-001", "UNCOMFORTABLE-HEADPHONES", qty=1, eta=None)
    different_sku_line = Orderline("order-123", "EXPENSIVE-IPAD", 100)
    assert batch.can_allocate(different_sku_line) is False


def test_deallocate() -> None:
    batch, line = make_batch_and_line("EXPENSIVE-HEADPHONES", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("SOMETHING", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20
