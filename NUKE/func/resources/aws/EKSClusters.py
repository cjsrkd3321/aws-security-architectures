from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import convert_dict_to_tags


class EKSCluster(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("list_clusters").paginate()
            clusters = [c for clusters in iterator for c in clusters["clusters"]]
            for cluster in clusters:
                try:
                    cluster = self.svc.describe_cluster(name=cluster)["cluster"]
                except self.exceptions.ResourceNotFoundException:
                    continue
                results.append(
                    {
                        "id": cluster["name"],
                        "name": cluster["name"],
                        "tags": convert_dict_to_tags(cluster.get("tags")),
                        "arn": cluster["arn"],
                        "state": cluster["status"],
                        "create_date": cluster["createdAt"],
                        "unique_id": cluster.get("id"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_cluster(name=resource["id"])
            return True, None
        except self.exceptions.ResourceNotFoundException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["state"] in ["DELETING"]:
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
    resources.append(EKSCluster)
