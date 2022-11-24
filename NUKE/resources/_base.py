from abc import ABCMeta, abstractmethod


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
