from ._base import ResourceBase
from . import resources, Config
from ._utils import get_name_from_tags

import boto3


class EC2NetworkInterface(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_network_interfaces").paginate()
            return [
                {
                    "id": (ni := network_interface)["NetworkInterfaceId"],
                    "tags": (tags := ni.get("TagSet")),
                    "name": get_name_from_tags(tags),
                    "state": [
                        ni["Attachment"]["Status"] if ni.get("Attachment") else None
                    ][0],
                }
                for network_interfaces in iterator
                for network_interface in network_interfaces["NetworkInterfaces"]
            ], None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_network_interface(NetworkInterfaceId=resource["id"])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
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


if __name__ != "__main__":
    resources.append(EC2NetworkInterface)
