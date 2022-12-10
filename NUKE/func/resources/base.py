from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from ._types import ListResults, RemoveResults, FilterResults


class ResourceBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, sess=None, default_filter_func=None) -> None:
        pass

    @abstractmethod
    def list(self) -> ListResults:
        pass

    @abstractmethod
    def remove(self, resource) -> RemoveResults:
        pass

    @abstractmethod
    def filter(self, resource, *filters) -> FilterResults:
        pass

    @abstractmethod
    def properties(self) -> None:
        pass


class StateBase(str, Enum):
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class ResourceState(StateBase):
    New = auto()
    Failed = auto()
    Removed = auto()
    Filtered = auto()
