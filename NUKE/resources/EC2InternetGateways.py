from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources


class EC2InternetGateway(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["ec2"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_internet_gateways").paginate()
            results += [
                {
                    "id": igw["InternetGatewayId"],
                    "tags": (tags := igw.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "is_attached": True if igw["Attachments"] else False,
                }
                for igws in iterator
                for igw in igws["InternetGateways"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_internet_gateway(InternetGatewayId=resource["id"])
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
    resources.append(EC2InternetGateway)
