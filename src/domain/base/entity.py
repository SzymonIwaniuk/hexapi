from domain.base.model import Model
from dataclasses import dataclass


@dataclass
class Entity(Model):
    """Base class for domain entitie objects."""

    def __str__(self):
        return f'{type(self).__name__}'

    def __repr__(self):
        return self.__str__()
