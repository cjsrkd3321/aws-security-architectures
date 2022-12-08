from resources import resources
from resources.base import ResourceBase
from resources.utils import get_name_from_tags


class EC2EgressOnlyInternetGateway(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator(
                "describe_egress_only_internet_gateways"
            ).paginate()
            results += [
                {
                    "id": eigw["EgressOnlyInternetGatewayId"],
                    "tags": (tags := eigw.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "unique_id": eigw["EgressOnlyInternetGatewayId"],
                }
                for eigws in iterator
                for eigw in eigws["EgressOnlyInternetGateways"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_egress_only_internet_gateway(
                EgressOnlyInternetGatewayId=resource["id"]
            )
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
    resources.append(EC2EgressOnlyInternetGateway)
