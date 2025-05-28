from __future__ import annotations


from typing import Set, Optional
from datetime import date
from uuid import UUID


from pydantic import BaseModel, Field, PositiveInt, field_validator, ConfigDict


class OrderLine(BaseModel):
    id: Optional[UUID] = Field(default=None)
    sku: str
    qty: PositiveInt  # Because qty is greater than 0
    orderid: str

    def __hash__(self):
        return hash((self.sku, self.qty, self.orderid))

    def __eq__(self, other):
        if not isinstance(other, OrderLine):
            return False

        return all((
            other.orderid == self.orderid,
            other.sku == self.sku,
            other.qty == self.qty,
        ))

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        json_schema_extra={
            'example': {
                'id': '12345678123456781234567812345678',
                'sku': 'SONY-HEADPHONES',
                'qty': 1,
                'orderid': 'order-123'
            }
        }
    )


class OrderLineWithAllocatedIn(OrderLine):
    allocated_in: Batch


class Batch(BaseModel):
    id: Optional[UUID] = Field(default=None)
    reference: str
    sku: str
    eta: Optional[date]
    purchased_quantity: int
    allocations: Set[OrderLine] = Field(default_factory=set)

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'id': '12345678123456781234567812345678',
                'reference': 'batch-001',
                'sku': 'SONY-HEADPHONES',
                'purchased_quantity': 1,
                'allocations': [
                    {
                        'id': '12345678123456781234567812345678',
                        'orderid': 'order-123',
                        'sku': 'SONY-HEADPHONES',
                        'qty': 1
                    }
                ]
            }
        }
    )

    @field_validator('allocations', mode='before')
    @classmethod
    def convert_to_set(cls, value):
        if isinstance(value, list):
            return set((OrderLine.model_validate(obj) for obj in value))

        return value
