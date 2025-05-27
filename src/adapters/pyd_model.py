from __future__ import annotations


from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field, PositiveInt, field_validator
from typing import Set, Optional


from domain import model


class OrderLine(BaseModel, model.OrderLine):
    id: Optional[UUID] = Field(default=None)
    sku: str
    qty: PositiveInt  # Because qty is greater than 0
    orderid: str

    def __hash__(self):
        return hash((self.sku, self.qty, self.orderid))

    def __eq__(self, other):
        if not isinstance(other, model.OrderLine):
            return False

        return all((
            other.orderid == self.orderid,
            other.sku == self.sku,
            other.qty == self.qty,
        ))

    class Config:
        from_attributes = True
        frozen = True

        schema_extra = {
            'example': {
                'id': '12345678123456781234567812345678',
                'sku': 'SONY-HEADPHONES',
                'qty': 1,
                'orderid': 'order-123'
            }
        }


class OrderLineWithAllocatedIn(OrderLine):
    allocated_in: Batch


class Batch(BaseModel, model.Batch):
    id: Optional[UUID] = Field(default=None)
    reference: str
    sku: str
    eta: Optional[date]
    purchased_quantity: int
    allocations: Set[OrderLine] = Field(default_factory=set)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            set: list
        }

        schema_extra = {
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

    @field_validator('allocations', mode='before')
    @classmethod
    def convert_to_set(cls, value):
        if isinstance(value, list):
            return set((OrderLine.model_validate(obj) for obj in value))

        return value
