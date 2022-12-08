from abc import ABCMeta, abstractmethod
from enum import Enum, auto


class ResourceBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, sess=None, default_filter_func=None):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def remove(self, resource):
        pass

    @abstractmethod
    def filter(self, resource, *filters):
        pass

    @abstractmethod
    def properties(self):
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
