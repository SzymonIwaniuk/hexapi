from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, Set
from .base.entity import Entity


@dataclass(unsafe_hash=True)
class Orderline(Entity):
    orderid: str
    sku: str
    qty: int


class Batch(Entity):
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[Orderline] = set()

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
