from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import mapper
from ..domain.batches import Orderline


metadata = MetaData()

order_lines = Table(
    'order_lines',
    metadata,
    Column("order_id", String(255), primary_key=True),
    Column("sku", String(255), primary_key=True),
    Column("qty", Integer),
)


def start_mappers():
    mapper(Orderline, order_lines)
