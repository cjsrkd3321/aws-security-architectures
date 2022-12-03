from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

import boto3


class EC2TransitGateway(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_transit_gateways").paginate()
            results += [
                {
                    "id": tgw["TransitGatewayId"],
                    "tags": (tags := tgw.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "unique_id": tgw["TransitGatewayId"],
                    "arn": tgw["TransitGatewayArn"],
                    "description": tgw.get("Description"),
                    "create_date": tgw["CreationTime"],
                    "state": tgw["State"],
                }
                for tgws in iterator
                for tgw in tgws["TransitGateways"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_transit_gateway(TransitGatewayId=resource["id"])[
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
    resources.append(EC2TransitGateway)
