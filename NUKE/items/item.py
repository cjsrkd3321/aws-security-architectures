from resources._base import ResourceState as rs


class Item:
    def __init__(self, resource, region, name, filterer, remover):
        self.__item = {
            "state": rs.New,
            "reason": None,
            "region": region,
            "resource": resource,
            "type": name,
        }
        self.__filterer = filterer
        self.__remover = remover

    def filter(self):
        is_filter, err = self.__filterer(self.__item["resource"])
        self.__item["state"] = rs.Filtered if is_filter else rs.New
        self.__item["reason"] = is_filter if is_filter else err

    def remove(self):
        is_removed, err = self.__remover(self.__item["resource"])
        self.__item["state"] = rs.Removed if is_removed else rs.Failed
        self.__item["reason"] = None if is_removed else err

    def is_skip(self):
        if self.__item["state"] in [rs.Filtered, rs.Removed]:
            return True
        return False

    @property
    def item(self):
        return self.__item

    @property
    def current(self):
        return f"{self.__item['region']} - {self.__item['type']} - {self.__item['resource']['id']} | {self.__item['state']} - {self.__item['reason']}"
