from http import HTTPStatus

from fastapi import FastAPI

from domain.services import allocate
from domain import model
from adapters.pyd_model import OrderLine
from src.repositories.repository import SqlAlchemyRepository

app = FastAPI()


@app.post("/allocate", status_code=HTTPStatus.ACCEPTED)
async def allocate_endpoint(line: OrderLine) -> dict[str, str]:
    session.start_session()
    batches = SqlAlchemyRepository.list()

    lines = model.OrderLine(line.orderid, line.sku, line.qty)

    batchref = allocate(lines, batches)

    session.commit()

    return {'status': 'Ok', "batchref": batchref}
