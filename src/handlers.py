from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from adapters.pyd_model import Batch, OrderLine
from domain import services
from repositories.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: List[Batch]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(line: OrderLine, repo: AbstractRepository, session: Session) -> str:
    """
    Allocate an order line to a batch.

    Args:
        line: The order line containing order ID, SKU, and quantity.
        repo: The repository to fetch available batches.
        session: The database session for committing changes.

    Raises:
        InvalidSku: If the sku in the order line is not valid.

    Returns:
        str: The reference id of the batch to which the order line was allocated.
    """

    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = services.allocate(line, batches)
    session.commit()
    return batchref
