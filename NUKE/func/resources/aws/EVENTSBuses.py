from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class EVENTSBus(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            buses = self.svc.list_event_buses()["EventBuses"]
            for bus in buses:
                name, arn = bus["Name"], bus["Arn"]
                try:
                    tags = self.svc.list_tags_for_resource(ResourceARN=arn)["Tags"]
                except self.exceptions.ResourceNotFoundException:
                    continue

                results.append(
                    {
                        "id": name,
                        "name": name,
                        "tags": tags,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_event_bus(Name=resource["id"])
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["name"] == "default":
            return f"DEFAULT(IMPOSSIBLE: {resource['name']})", None
        if self.filter_func:
            try:
                if self.filter_func(resource):
                    return self.filter_func.__name__, None
            except Exception as e:
                return False, e
        for filter in filters:
            if filter(resource):
                return filter.__name__, None
        return False, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(EVENTSBus)
