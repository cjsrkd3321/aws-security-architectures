from resources import resources
from resources.base import ResourceBase


class RDSCluster(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["rds"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_db_clusters").paginate()
            clusters = [c for clusters in iterator for c in clusters["DBClusters"]]
            for cluster in clusters:
                results.append(
                    {
                        "id": cluster["DBClusterIdentifier"],
                        "name": cluster["DatabaseName"],
                        "tags": cluster["TagList"],
                        "state": cluster["Status"],
                        "unique_id": cluster["DbClusterResourceId"],
                        "is_public_access": cluster.get("PubliclyAccessible"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_db_cluster(
                DBClusterIdentifier=resource["id"], SkipFinalSnapshot=True
            )
            return True, None
        except self.exceptions.DBClusterNotFoundFault:
            return True, None
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
    resources.append(RDSCluster)
