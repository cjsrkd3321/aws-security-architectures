from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class EMRCluster(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("list_clusters").paginate()
            clusters = [c for clusters in iterator for c in clusters["Clusters"]]
            for cluster in clusters:
                cluster_id = cluster["Id"]
                cluster = self.svc.describe_cluster(ClusterId=cluster_id)["Cluster"]
                results.append(
                    {
                        "id": cluster_id,
                        "name": cluster["Name"],
                        "tags": cluster.get("Tags", []),
                        "arn": cluster["ClusterArn"],
                        "state": (s := cluster["Status"])["State"],
                        "create_date": (t := s["Timeline"]).get("CreationDateTime"),
                        "delete_date": t.get("EndDateTime"),
                        "unique_id": cluster_id,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.terminate_job_flows(JobFlowIds=[resource["id"]])
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["state"].startswith("TERMINAT"):
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
    resources.append(EMRCluster)
