import pytest

import handlers
from adapters import pyd_model
from repositories import repository


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_commits():
    line = pyd_model.OrderLine(orderid="o1", sku="CASEPHONE", qty=10)
    batch = pyd_model.Batch(reference="b1", sku="CASEPHONE", purchased_quantity=100, eta=None)
    repo = repository.FakeRepository([batch])
    session = FakeSession()

    await handlers.allocate(line, repo, session)
    assert session.committed is True


@pytest.mark.asyncio
async def test_returns_allocations() -> None:
    line = pyd_model.OrderLine(orderid="o1", sku="KEYBOARD", qty=2)
    batch = pyd_model.Batch(reference="b1", sku="KEYBOARD", purchased_quantity=100, eta=None)
    repo = repository.FakeRepository([batch])

    result = await handlers.allocate(line, repo, FakeSession())
    assert result == "b1"


@pytest.mark.asyncio
async def test_error_for_invalid_sku() -> None:
    line = pyd_model.OrderLine(orderid="o1", sku="NONEXISTENTSKU", qty=10)
    batch = pyd_model.Batch(reference="b1", sku="AREALSKU", purchased_quantity=100, eta=None)
    repo = repository.FakeRepository([batch])

    with pytest.raises(handlers.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        await handlers.allocate(line, repo, FakeSession())
