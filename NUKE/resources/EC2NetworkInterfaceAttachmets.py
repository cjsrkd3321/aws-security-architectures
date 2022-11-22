from ._base import ResourceBase
from . import resources, Config
from ._utils import get_name_from_tags

import boto3


class EC2NetworkInterfaceAttachmet(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_network_interfaces").paginate()
            return [
                {
                    "id": [
                        ni["Attachment"]["AttachmentId"]
                        if (ni := network_interface).get("Attachment")
                        else None
                    ][0],
                    "tags": (tags := ni.get("TagSet")),
                    "name": get_name_from_tags(tags),
                    "state": ni["Status"],
                }
                for network_interfaces in iterator
                for network_interface in network_interfaces["NetworkInterfaces"]
            ], None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_network_interface(
                    AttachmentId=resource["id"], Force=True
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resources, filter_func=None):
        if not resources:
            return [], None
        filtered_resources = [
            r for r in resources if not r.get("state").startswith("detach")
        ]
        if filter_func:
            try:
                filtered_resources = filter_func(filtered_resources)
            except Exception as e:
                return [], e
        return filtered_resources, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(EC2NetworkInterfaceAttachmet)
