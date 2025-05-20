from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, Set, NewType, List
from .base.value_object import ValueObject
from .base.entity import Entity
from .exceptions import OutOfStock


# type hints
Quantity = NewType('Quantity', int)
Sku = NewType('Sku', str)
Reference = NewType('Reference', str)


def allocate(line: Orderline, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference

    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")


@dataclass(unsafe_hash=True)
class Orderline(ValueObject):
    orderid: str
    sku: str
    qty: int


class Batch(Entity):
    def __init__(
            self,
            ref: Reference,
            sku: Sku,
            qty: Quantity,
            eta: Optional[date]
    ) -> None:

        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[Orderline] = set()

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: Orderline) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: Orderline) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: Orderline) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity
