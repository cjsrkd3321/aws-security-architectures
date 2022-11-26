from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources, Config

import boto3


class EC2Instance(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_instances").paginate()
            return [
                {
                    "id": (i := instance)["InstanceId"],
                    "tags": (tags := i.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "state": i["State"]["Name"],
                    "type": i["InstanceType"],
                    "create_date": i["LaunchTime"],
                    "architecture": i.get("Architecture"),
                    "instance_profile": i.get("IamInstanceProfile"),
                    "lifecycle": i["InstanceLifecycle"],
                    "security_groups": i.get("SecurityGroups"),
                    "cpu_core_count": i["CpuOptions"]["CoreCount"],
                    "platform": i.get("Platform"),
                }
                for instances in iterator
                for reservations in instances["Reservations"]
                for instance in reservations["Instances"]
            ], None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.terminate_instances(InstanceIds=[resource["id"]])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resources, *filters):
        if not resources:
            return [], None
        filtered_resources = [
            r for r in resources if not r["state"] in ["shutting-down", "terminated"]
        ]
        if self.filter_func:
            try:
                filtered_resources = self.self.filter_func(filtered_resources)
            except Exception as e:
                return [], e
        for filter in filters:
            filtered_resources = filter(filtered_resources)
        return filtered_resources, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(EC2Instance)
