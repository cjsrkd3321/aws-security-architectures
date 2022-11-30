from ._base import ResourceBase
from . import resources, Config
from ._utils import get_name_from_tags

import boto3


class EC2NetworkInterfaceAttachmet(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_network_interfaces").paginate()
            return [
                {
                    "id": (ni := network_interface)["Attachment"]["AttachmentId"],
                    "tags": (tags := ni.get("TagSet")),
                    "name": get_name_from_tags(tags),
                    "state": ni["Attachment"]["Status"],
                    "create_date": ni["Attachment"].get("AttachTime"),
                    "delete_on_termination": ni["Attachment"]["DeleteOnTermination"],
                }
                for network_interfaces in iterator
                for network_interface in network_interfaces["NetworkInterfaces"]
                if "Attachment" in network_interface
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

    def filter(self, resource, *filters):
        if resource["delete_on_termination"]:
            return "DEFAULT(INSTANCE DEPENDENCY)", None
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
    resources.append(EC2NetworkInterfaceAttachmet)
