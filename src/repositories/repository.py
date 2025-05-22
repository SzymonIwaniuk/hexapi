from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from domain.order.entities import Batch


class AbstractRepository(ABC):
    """
      Abstract base class for batch repositories.

      Defines the interface for repository implementations that handle storage
      and retrieval of Batch entities.

      Subclasses must implement methods to add a batch, get a batch by its
      reference, and list all batches.

      Methods:
          add(batch: Batch) -> None:
              Add a Batch instance to the repository.

          get(reference: str) -> Batch:
              Retrieve a Batch by its unique reference.

          list() -> List[Batch]:
              Return a list of all stored Batch instances.
      """

    @abstractmethod
    async def add(self, batch: Batch) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, reference: str) -> Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, batch: Batch) -> None:
        self.session.add(batch)

    def get(self, reference: str) -> Batch:
        return self.session.query(Batch).filter_by(reference=reference).one()

    def list(self) -> List[Batch]:
        """List all batches in the repository."""
        return self.session.query(Batch).all()
