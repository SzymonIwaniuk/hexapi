import uuid
import pytest
import requests

import config


def random_suffix() -> str:
    return uuid.UUID.hex[:6]


def random_sku(name="") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name="") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name="") -> str:
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock):
    sku, othersku = random_sku(), random_sku("other")

    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    add_stock(
        [
            (laterbatch, sku, 100, "2025-05-27"),
            (earlybatch, sku, 100, "2025-05-26"),
            (otherbatch, othersku, 100, "None"),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    response = requests.post(f"{url}/allocate", json=data)

    assert response.status_code == 202
    assert response.json()['status'] == 'Ok'
    assert response.json()["batchref"] == earlybatch

