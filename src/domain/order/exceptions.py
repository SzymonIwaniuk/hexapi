from domain.base.exceptions import BaseMsgException


class OutOfStock(BaseMsgException):
    """Out of stock exception for allocate fn"""

    def __init__(self, sku: str):
        self.message = f"Out of stock for sku {sku}"
