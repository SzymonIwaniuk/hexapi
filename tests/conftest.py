import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.orm.session import Session
from sqlalchemy.engine import Engine


from dbschema.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db() -> Engine:
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db: Engine) -> Session:
    start_mappers()
    db_session = sessionmaker(bind=in_memory_db)
    yield db_session()
    clear_mappers()
