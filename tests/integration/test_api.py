import uuid
import pytest


from http import HTTPStatus


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name="") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name="") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name="") -> str:
    return f"order-{name}-{random_suffix()}"


@pytest.mark.asyncio
async def test_health_check(async_test_client) -> None:
    response = await async_test_client.get("/health_check")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "Ok"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("restart_api")
async def test_api_returns_allocation(async_test_client, add_stock) -> None:
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
    response = await async_test_client.post("/allocate", json=data)
    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json() == {"status": "Ok", "batchref": earlybatch}
