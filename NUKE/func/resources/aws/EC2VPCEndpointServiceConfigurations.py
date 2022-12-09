from resources import resources
from resources.base import ResourceBase
from resources.utils import get_name_from_tags


class EC2VPCEndpointServiceConfiguration(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator(
                "describe_vpc_endpoint_service_configurations"
            ).paginate()
            cnfs = [cnf for cnfs in iterator for cnf in cnfs["ServiceConfigurations"]]
            for cnf in cnfs:
                svc_id = cnf["ServiceId"]
                conns = self.svc.describe_vpc_endpoint_connections(
                    Filters=[{"Name": "service-id", "Values": [svc_id]}]
                )["VpcEndpointConnections"]
                results.append(
                    {
                        "id": svc_id,
                        "tags": (tags := cnf.get("Tags", [])),
                        "name": get_name_from_tags(tags),
                        "service_name": cnf["ServiceName"],
                        "state": cnf["ServiceState"],
                        "vpc_endpoint_ids": [conn["VpcEndpointId"] for conn in conns],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            unsuccess = self.svc.reject_vpc_endpoint_connections(
                ServiceId=resource["id"], VpcEndpointIds=resource["vpc_endpoint_ids"]
            )["Unsuccessful"]
            if unsuccess:
                return False, unsuccess[0]["Error"]["Code"]

            unsuccess = self.svc.delete_vpc_endpoint_service_configurations(
                ServiceIds=[resource["id"]]
            )["Unsuccessful"]
            if not unsuccess:
                return True, None
            else:
                return False, unsuccess[0]["Error"]["Code"]
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["state"].startswith("Delet"):
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
    resources.append(EC2VPCEndpointServiceConfiguration)
