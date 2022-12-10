from resources import resources
from resources.base import ResourceBase


class EC2RouteTable(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            pairs = self.svc.describe_route_tables()["RouteTables"]
            for pair in pairs:
                results.append(
                    {
                        "id": pair["RouteTableId"],
                        "tags": pair.get("Tags", []),
                        "name": pair["RouteTableId"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_route_table(RouteTableId=resource["id"])
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
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
    resources.append(EC2RouteTable)
