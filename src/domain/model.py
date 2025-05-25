from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Set, NewType


# type hints
Quantity = NewType('Quantity', int)
Sku = NewType('Sku', str)
Reference = NewType('Reference', str)


@dataclass(unsafe_hash=True)
class OrderLine:
    """
        Represents a request for a quantity of a specific product (sku)
        in a customer's order.
    """

    orderid: str
    sku: str
    qty: int


class Batch:
    """
        Represents a delivery of a specific product available for allocation
        to customer orders.
    """

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
        self._allocations: Set[OrderLine] = set()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self) -> int:
        return hash(self.reference)

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity
