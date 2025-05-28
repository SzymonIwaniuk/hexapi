from http import HTTPStatus


from fastapi import FastAPI
from sqlalchemy.orm import Session


from domain.services import allocate
from adapters.pyd_model import OrderLine
from repositories import repository
from domain import model


def make_app(test_db: Session = None) -> FastAPI:
    app = FastAPI()

    @app.get("/health_check")
    async def health_check(status_code=HTTPStatus.OK) -> dict[str, str]:
        return {"status": "Ok"}

    @app.post("/allocate", status_code=HTTPStatus.ACCEPTED)
    async def allocate_endpoint(
        lines: OrderLine,
    ) -> dict[str, str]:

        line = model.OrderLine(lines.orderid, lines.sku, lines.qty)
        repo = repository.SqlAlchemyRepository(test_db)
        batches = repo.list()

        batchref = allocate(line, batches)

        return {"status": 'Ok', "batchref": batchref}

    return app
