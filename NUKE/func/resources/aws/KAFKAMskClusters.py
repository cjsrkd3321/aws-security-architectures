from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import convert_dict_to_tags


class KAFKAMskCluster(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("list_clusters_v2").paginate()
            clusters = [
                cluster
                for clusters in iterator
                for cluster in clusters["ClusterInfoList"]
            ]
            for cluster in clusters:
                results.append(
                    {
                        "id": cluster["ClusterArn"],
                        "name": cluster["ClusterName"],
                        "tags": convert_dict_to_tags(cluster.get("Tags")),
                        "arn": cluster["ClusterArn"],
                        "state": cluster["State"],
                        "create_date": cluster["CreationTime"],
                        "type": cluster["ClusterType"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_cluster(ClusterArn=resource["id"])
            return True, None
        except self.exceptions.NotFoundException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["state"] in ["DELETING", "CREATING"]:
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
    resources.append(KAFKAMskCluster)
