from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import get_name_from_tags


class EC2TransitGatewayAttachment(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator(
                "describe_transit_gateway_attachments"
            ).paginate()
            results += [
                {
                    "id": tgw["TransitGatewayAttachmentId"],
                    "tags": (tags := tgw.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "create_date": tgw["CreationTime"],
                    "type": tgw["ResourceType"],
                    "unique_id": tgw["TransitGatewayAttachmentId"],
                    "state": tgw["State"],
                }
                for tgws in iterator
                for tgw in tgws["TransitGatewayAttachments"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_transit_gateway_vpc_attachment(
                TransitGatewayAttachmentId=resource["id"]
            )
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
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
    resources.append(EC2TransitGatewayAttachment)
