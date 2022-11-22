from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

import boto3


class EC2Subnet(ResourceBase):
    def __init__(self, region="ap-northeast-2"):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_subnets").paginate()
            return [
                {
                    "id": subnet["SubnetId"],
                    "tags": (tags := subnet.get("Tags")),
                    "name": get_name_from_tags(tags),
                    "state": subnet["State"],
                }
                for subnets in iterator
                for subnet in subnets["Subnets"]
            ], None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_subnet(SubnetId=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resources, filter_func=None):
        if not resources:
            return [], None
        filtered_resources = resources
        if filter_func:
            try:
                filtered_resources = filter_func(filtered_resources)
            except Exception as e:
                return [], e
        return filtered_resources, None

    def properties(self):
        pass


if __name__ == "__main__":
    vpc = EC2Subnet()
    print(vpc.filter(vpc.list()))
else:
    resources.append(EC2Subnet)
