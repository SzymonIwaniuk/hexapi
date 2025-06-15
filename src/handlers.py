from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from domain.model import Batch, OrderLine
from domain import services
from repositories.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: List[Batch]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(line: OrderLine, repo: AbstractRepository, session: Session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = services.allocate(line, batches)
    session.commit()
    return batchref
