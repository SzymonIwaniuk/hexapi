from abc import ABC, abstractmethod


class Entity(ABC):
    """Base class for domain entitie objects."""

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass
