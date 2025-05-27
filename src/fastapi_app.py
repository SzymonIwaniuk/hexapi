from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated


from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from domain.services import allocate
from adapters.pyd_model import OrderLine
from dbschema import orm
from repositories import repository
from domain import model


import config


async def setup_postgres(app: FastAPI):
    db_uri = config.get_db_uri()
    engine = create_async_engine(db_uri, echo=True)
    app.state.postgres = engine
    app.state.sessionmaker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        )


async def shutdown_postgres(app: FastAPI):
    engine = app.state.postgres
    engine.dispose()


async def get_db(request: Request) -> AsyncSession:
    SessionLocal = request.app.state.sessionmaker
    async with SessionLocal() as session:
        yield session


db_dependency = Annotated[AsyncSession, Depends(get_db)]


def make_app(test_db: bool = False) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        orm.start_mappers()
        await setup_postgres(app)
        yield
        await shutdown_postgres(app)

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health_check")
    async def health_check() -> dict[str, str]:
        return {"status": "Ok"}

    @app.post("/allocate", status_code=HTTPStatus.ACCEPTED)
    async def allocate_endpoint(
        lines: OrderLine,
        client_db: db_dependency,
    ) -> dict[str, str]:

        line = model.OrderLine(lines.orderid, lines.sku, lines.qty)
        batches = repository.SqlAlchemyRepository(client_db).list()

        batchref = allocate(line, batches)

        await client_db.commit()

        return {"status": 'Ok', "batchref": batchref}

    return app
