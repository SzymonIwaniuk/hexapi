from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import registry
from domain.batches import Orderline

mapper_registry = registry()
metadata = MetaData()

order_lines = Table(
    'order_lines',
    metadata,
    Column("orderid", String(255), primary_key=True),
    Column("sku", String(255), primary_key=True),
    Column("qty", Integer),
)


def start_mappers():
    mapper_registry.map_imperatively(Orderline, order_lines)
