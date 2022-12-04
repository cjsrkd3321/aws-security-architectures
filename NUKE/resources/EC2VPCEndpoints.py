from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources


class EC2VPCEndpoint(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess["ec2"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_vpc_endpoints").paginate()
            vpces = [vpce for vpces in iterator for vpce in vpces["VpcEndpoints"]]
            for vpce in vpces:
                results.append(
                    {
                        "id": vpce["VpcEndpointId"],
                        "type": vpce["VpcEndpointType"],
                        "vpc_id": vpce["VpcId"],
                        "state": vpce["State"],
                        "tags": (tags := vpce.get("Tags", [])),
                        "name": get_name_from_tags(tags),
                        "create_date": vpce["CreationTimestamp"],
                        "service_name": vpce["ServiceName"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_vpc_endpoints(VpcEndpointIds=[resource["id"]])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
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
    resources.append(EC2VPCEndpoint)
