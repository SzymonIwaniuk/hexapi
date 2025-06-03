from http import HTTPStatus
from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

import handlers
from adapters.pyd_model import Batch, OrderLine
from domain import events, model
from domain.services import allocate
from repositories import repository


def make_app(test_db: Session = None) -> FastAPI:
    app = FastAPI()

    @app.get("/health_check", status_code=HTTPStatus.OK)
    async def health_check() -> dict[str, str]:
        return {"status": "Ok"}

    @app.post("/allocate", status_code=HTTPStatus.ACCEPTED)
    async def allocate_endpoint(
        lines: OrderLine,
    ) -> dict[str, str]:

        line = model.OrderLine(lines.orderid, lines.sku, lines.qty)
        repo = repository.SqlAlchemyRepository(test_db)

        try:
            batchref = await handlers.allocate(line, repo, test_db)
        except (events.OutOfStock, handlers.InvalidSku) as e:
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail=str(e))
        return {"status": "Ok", "batchref": batchref}

    return app
