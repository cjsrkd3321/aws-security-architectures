from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import get_name_from_tags


class EC2NetworkInterface(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("describe_network_interfaces").paginate()
            results += [
                {
                    "id": (ni := network_interface)["NetworkInterfaceId"],
                    "tags": (tags := ni.get("TagSet")),
                    "name": get_name_from_tags(tags),
                    "state": ni["Status"],
                    "type": ni["InterfaceType"],
                    "attachment": ni.get("Attachment", {}),
                    "requester_id": ni.get("RequesterId"),
                    "description": ni.get("Description", ""),
                }
                for network_interfaces in iterator
                for network_interface in network_interfaces["NetworkInterfaces"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            if resource["attachment"]:
                self.svc.detach_network_interface(
                    AttachmentId=resource["id"], Force=True
                )
            self.svc.delete_network_interface(NetworkInterfaceId=resource["id"])
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["attachment"].get("DeleteOnTermination"):
            return "DEFAULT(INSTANCE DEPENDENCY)", None
        if resource["requester_id"] and resource["state"] != "available":
            return f"DEFAULT(REQUESTER DEPENDENCY {resource['requester_id']})", None
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
    resources.append(EC2NetworkInterface)
