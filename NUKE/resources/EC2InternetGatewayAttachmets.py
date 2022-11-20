from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

import boto3


class EC2InternetGatewayAttachmet(ResourceBase):
    def __init__(self, region="ap-northeast-2"):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            paginator = self.svc.get_paginator("describe_internet_gateways")
            iterator = paginator.paginate()
            if not iterator:
                return []
            return [
                {
                    "id": igw["InternetGatewayId"],
                    "tags": igw.get("Tags"),
                    "name": get_name_from_tags(igw.get("Tags")),
                    "state": a[0]["State"] if (a := igw["Attachments"]) else None,
                    "vpc_id": a[0]["VpcId"] if a else None,
                }
                for igws in iterator
                for igw in igws["InternetGateways"]
            ]
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_internet_gateway(
                    InternetGatewayId=resource["id"], VpcId=resource["vpc_id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            )
        except Exception as e:
            return e

    def filter(self, resources, filter_func=None):
        if not resources:
            return []
        filtered_resources = [
            r for r in resources if (s := r["state"]) and not s.startswith("detach")
        ]
        if filter_func:
            filtered_resources = filter_func(filtered_resources)
        return filtered_resources

    def properties(self):
        pass


if __name__ == "__main__":
    vpc = EC2InternetGatewayAttachmet()
    print(vpc.filter(vpc.list()))
else:
    resources.append(EC2InternetGatewayAttachmet)
