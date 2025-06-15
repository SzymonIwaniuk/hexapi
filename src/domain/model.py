from __future__ import annotations

from datetime import date
from typing import NewType, Optional, Set
from uuid import UUID

from pydantic import BaseModel, PositiveInt, Field, ConfigDict, field_validator


# type hints
Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)
OrderId = NewType("OrderId", str)


class OrderLine(BaseModel):
    """
    Represents a request for a quantity of a specific product (sku)
    in a customer's order.
    """

    id: Optional[UUID] = Field(default=None)
    sku: Sku
    qty: PositiveInt  # Because qty is greater than 0
    orderid: OrderId

    def __hash__(self):
        return hash((self.sku, self.qty, self.orderid))

    def __eq__(self, other):
        if not isinstance(other, OrderLine):
            return False

        return all(
            (
                other.orderid == self.orderid,
                other.sku == self.sku,
                other.qty == self.qty,
            )
        )

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        json_schema_extra={
            "example": {
                "id": "12345678123456781234567812345678",
                "sku": "SONY-HEADPHONES",
                "qty": 1,
                "orderid": "order-123",
            }
        },
    )


class OrderLineWithAllocatedIn(OrderLine):
    """
    Represents a customer order line that has been allocated to a specific batch
    """
    allocated_in: Batch


class Batch(BaseModel):
    """
    Represents a delivery of a specific product available for allocation
    to customer orders.
    """

    id: Optional[UUID] = Field(default=None)
    reference: Reference
    sku: Sku
    eta: Optional[date]
    purchased_quantity: PositiveInt
    allocations: Set[OrderLine] = Field(default_factory=set)

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
            self.allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self.allocations:
            self.allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self.allocations)

    @property
    def available_quantity(self) -> int:
        return self.purchased_quantity - self.allocated_quantity

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "12345678123456781234567812345678",
                "reference": "batch-001",
                "sku": "SONY-HEADPHONES",
                "purchased_quantity": 1,
                "allocations": [
                    {
                        "id": "12345678123456781234567812345678",
                        "orderid": "order-123",
                        "sku": "SONY-HEADPHONES",
                        "qty": 1,
                    }
                ],
            }
        }
    )

    @field_validator("allocations", mode="before")
    @classmethod
    def convert_to_set(cls, value):
        if isinstance(value, list):
            return set((OrderLine.model_validate(obj) for obj in value))

        return value
