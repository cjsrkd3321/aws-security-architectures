from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

from .EC2VPC import EC2VPC

import boto3


class EC2VPCEndpoint(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_vpc_endpoints").paginate()
            vpces = [vpce for vpces in iterator for vpce in vpces["VpcEndpoints"]]
            for vpce in vpces:
                results.append(
                    {
                        "id": vpce["VpcEndpointId"],
                        "type": vpce["VpcEndpointType"],
                        "vpc_id": vpce["VpcId"],
                        "state": vpce["State"],
                        "name": vpce["ServiceName"],
                        "tags": vpce.get("Tags", []),
                        "create_date": vpce["CreationTimestamp"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_vpc_endpoints(VpcEndpointIds=[resource["id"]])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["state"].startswith("delet"):
            return f"DEFAULT(IMPOSSIBLE: {resource['state']})", None
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
    resources.append(EC2VPCEndpoint)
