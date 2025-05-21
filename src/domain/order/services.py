from domain.order.entities import Batch
from domain.order.value_objects import OrderLine
from domain.order.exceptions import OutOfStock
from typing import List


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference

    except StopIteration:
        raise OutOfStock(line.sku)
