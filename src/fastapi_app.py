from http import HTTPStatus
from typing import List


from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session


from domain.services import allocate
from adapters.pyd_model import OrderLine, Batch
from repositories import repository
from domain import model
from domain import events


def is_valid_sku(sku: str, batches: List[Batch]) -> bool:
    return sku in {b.sku for b in batches}


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
        batches = repo.list()

        if not is_valid_sku(line.sku, batches):
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"Invalid sku {line.sku}")
        try:
            batchref = allocate(line, batches)
        except events.OutOfStock as e:
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail=str(e))
        return {"status": 'Ok', "batchref": batchref}

    return app
