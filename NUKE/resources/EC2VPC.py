from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

import boto3


class EC2VPC(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_vpcs").paginate()
            return [
                {
                    "id": vpc["VpcId"],
                    "tags": (tags := vpc.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "is_default": vpc["IsDefault"],
                    "state": vpc["State"],
                }
                for vpcs in iterator
                for vpc in vpcs["Vpcs"]
            ], None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_vpc(VpcId=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
                == 200
            ), None
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
    resources.append(EC2VPC)
