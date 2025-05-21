from sqlalchemy import Table, MetaData, Column, Integer, String, Date
from sqlalchemy.orm import registry
from domain.order.value_objects import Orderline
from domain.order.entities import Batch


mapper_registry = registry()
metadata = MetaData()

order_lines = Table(
    'order_lines',
    metadata,
    Column("orderid", String(255), primary_key=True),
    Column("sku", String(255), primary_key=True),
    Column("qty", Integer),
)

batches = Table(
    "batches",
    metadata,
    Column("reference", String(255), primary_key=True),
    Column("sku", String(255), primary_key=True),
    Column("_purchased_qty", Integer),
    Column("eta", Date),
)

def start_mappers():
    mapper_registry.map_imperatively(Orderline, order_lines)
    mapper_registry.map_imperatively(Batch, batches)