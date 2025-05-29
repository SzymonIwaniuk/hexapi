import uuid
from http import HTTPStatus
from typing import Callable


import pytest
from httpx import AsyncClient


import config


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name="") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name="") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name="") -> str:
    return f"order-{name}-{random_suffix()}"


@pytest.mark.asyncio
async def test_health_check(async_test_client: AsyncClient) -> None:
    response = await async_test_client.get("/health_check")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "Ok"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("restart_api")
async def test_api_returns_allocation(async_test_client: AsyncClient, add_stock: Callable) -> None:
    sku, othersku = random_sku(), random_sku("other")

    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    add_stock(
        [
            (laterbatch, sku, 100, "2025-05-27"),
            (earlybatch, sku, 100, "2025-05-26"),
            (otherbatch, othersku, 100, None),
        ]
    )

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()
    response = await async_test_client.post(f"{url}/allocate", json=data)
    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json() == {"status": "Ok", "batchref": earlybatch}


@pytest.mark.asyncio
@pytest.mark.usefixtures("restart_api")
async def test_allocations_are_persisted(async_test_client: AsyncClient, add_stock: Callable) -> None:
    sku = random_sku()
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)
    add_stock(
        [(batch1, sku, 10, "2025-05-29"), (batch2, sku, 100, "2025-05-30"),],
    )
    line1 = {"orderid": order1, "sku": sku, "qty": 10}
    line2 = {"orderid": order2, "sku": sku, "qty": 10}
    url = config.get_api_url()

    # first order uses up all stock in batch 1
    r = await async_test_client.post(f"{url}/allocate", json=line1)
    assert r.status_code == HTTPStatus.ACCEPTED
    assert r.json() == {"status": "Ok", "batchref": batch1}

    # second should go to batch 2
    r = await async_test_client.post(f"{url}/allocate", json=line2)
    assert r.status_code == HTTPStatus.ACCEPTED
    assert r.json() == {"status": "Ok", "batchref": batch2}
