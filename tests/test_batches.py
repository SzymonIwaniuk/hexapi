from model import Batch, Orderline
from datetime import date


def test_allocating_to_a_batch_reduces_available_quantity() -> None:
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = Orderline("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18