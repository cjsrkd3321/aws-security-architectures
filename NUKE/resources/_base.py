from abc import ABCMeta, abstractmethod
from enum import Enum


class ResourceBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def remove(self, resource):
        pass

    @abstractmethod
    def filter(self, resources, *filters):
        pass

    @abstractmethod
    def properties(self):
        pass


class StateBase(str, Enum):
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
