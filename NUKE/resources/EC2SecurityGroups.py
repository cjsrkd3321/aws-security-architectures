from ._base import ResourceBase
from . import resources, Config

import boto3


class EC2SecurityGroup(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            paginator = self.svc.get_paginator("describe_security_groups")
            iterator = paginator.paginate()
            if not iterator:
                return []
            return [
                {
                    "id": (sg := security_group)["GroupId"],
                    "name": sg["GroupName"],
                    "tags": sg.get("Tags"),
                }
                for security_groups in iterator
                for security_group in security_groups["SecurityGroups"]
            ]
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_security_group(
                    GroupId=resource["id"], GroupName=resource["name"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            )
        except Exception as e:
            return e

    def filter(self, resources, filter_func=None):
        if not resources:
            return []
        filtered_resources = [r for r in resources if r["name"] != "default"]
        if filter_func:
            filtered_resources = filter_func(filtered_resources)
        return filtered_resources

    def properties(self):
        pass


if __name__ == "__main__":
    sg = EC2SecurityGroup()
    print(sg.filter(sg.list()))
else:
    resources.append(EC2SecurityGroup)
