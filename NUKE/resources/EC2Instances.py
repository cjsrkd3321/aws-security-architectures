from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

import boto3


class EC2Instance(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            paginator = self.svc.get_paginator("describe_instances")
            iterator = paginator.paginate()
            if not iterator:
                return []
            return [
                {
                    "id": (i := instance)["InstanceId"],
                    "tags": (tags := i.get("Tags")),
                    "name": get_name_from_tags(tags),
                    "state": i["State"]["Name"],
                }
                for instances in iterator
                for reservations in instances["Reservations"]
                for instance in reservations["Instances"]
            ]
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.terminate_instances(InstanceIds=[resource["id"]])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            )
        except Exception as e:
            return e

    def filter(self, resources, filter_func=None):
        if not resources:
            return []
        filtered_resources = [
            r for r in resources if not r["state"] in ["shutting-down", "terminated"]
        ]
        if filter_func:
            filtered_resources = filter_func(filtered_resources)
        return filtered_resources

    def properties(self):
        pass


if __name__ == "__main__":
    vpc = EC2Instance()
    print(vpc.filter(vpc.list()))
else:
    resources.append(EC2Instance)
