from dataclasses import dataclass


@dataclass
class OutOfStock(Exception):
    sku: str
