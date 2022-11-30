from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

from .EC2VPC import EC2VPC

import boto3


class EC2InternetGatewayAttachmet(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            ec2_vpc = EC2VPC(default_filter_func=self.filter_func)
            vpcs, err = ec2_vpc.list(has_cache=True)
            if err:
                return results, err

            for vpc in vpcs:
                reason, err = ec2_vpc.filter(vpc)
                if err or reason:
                    continue

                vpc_id = vpc["id"]
                igws = self.svc.describe_internet_gateways(
                    Filters=[
                        {
                            "Name": "attachment.vpc-id",
                            "Values": [vpc_id],
                        }
                    ]
                )
                if not igws:
                    return results, None

                results += [
                    {
                        "id": igw["InternetGatewayId"],
                        "name": get_name_from_tags(igw.get("Tags", [])),
                        "state": igw["Attachments"][0]["State"],
                        "vpc_id": vpc_id,
                    }
                    for igw in igws["InternetGateways"]
                    if igw.get("Attachments")
                ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_internet_gateway(
                    InternetGatewayId=resource["id"], VpcId=resource["vpc_id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
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
    resources.append(EC2InternetGatewayAttachmet)
