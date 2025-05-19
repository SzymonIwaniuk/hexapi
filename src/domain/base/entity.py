from .model import Model
from abc import abstractmethod


class Entity(Model):
    """Base class for domain entitie objects."""

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass
