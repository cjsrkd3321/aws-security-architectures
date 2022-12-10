from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import convert_dict_to_tags


class EKSNodeGroup(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        from .EKSClusters import EKSCluster

        results: list = []
        try:
            eks_clusters = EKSCluster(self.svc, self.filter_func)
            clusters, err = eks_clusters.list()
            if err:
                return results, err

            for cluster in clusters:
                cluster_name = cluster["name"]
                try:
                    iterator = self.svc.get_paginator("list_nodegroups").paginate(
                        clusterName=cluster_name
                    )
                except self.exceptions.ResourceNotFoundException:
                    continue
                node_groups = [ng for grps in iterator for ng in grps["nodegroups"]]
                for node_group in node_groups:
                    try:
                        node_group = self.svc.describe_nodegroup(
                            clusterName=cluster_name, nodegroupName=node_group
                        )["nodegroup"]
                    except self.exceptions.ResourceNotFoundException:
                        continue

                    results.append(
                        {
                            "id": node_group["nodegroupName"],
                            "name": node_group["nodegroupName"],
                            "cluster_name": node_group["clusterName"],
                            "tags": convert_dict_to_tags(node_group.get("tags")),
                            "arn": node_group["nodegroupArn"],
                            "state": node_group["status"],
                            "create_date": node_group.get("createdAt"),
                            "last_modified_date": node_group.get("modifiedAt"),
                            "unique_id": node_group.get("id"),
                        }
                    )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_nodegroup(
                nodegroupName=resource["id"], clusterName=resource["cluster_name"]
            )
            return True, None
        except self.exceptions.ResourceNotFoundException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["state"] == "DELETING":
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
    resources.append(EKSNodeGroup)
