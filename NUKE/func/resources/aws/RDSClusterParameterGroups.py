from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class RDSClusterParameterGroup(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator(
                "describe_db_cluster_parameter_groups"
            ).paginate()
            param_groups = [
                pg
                for param_groups in iterator
                for pg in param_groups["DBClusterParameterGroups"]
            ]
            for param_group in param_groups:
                name = param_group["DBClusterParameterGroupName"]
                arn = param_group["DBClusterParameterGroupArn"]
                tags = self.svc.list_tags_for_resource(ResourceName=arn)["TagList"]
                results.append(
                    {
                        "id": name,
                        "name": name,
                        "tags": tags,
                        "description": param_group.get("Description"),
                        "arn": arn,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_db_cluster_parameter_group(
                DBClusterParameterGroupName=resource["id"]
            )
            return True, None
        except self.exceptions.DBParameterGroupNotFoundFault:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["id"].startswith("default."):
            return f"DEFAULT(IMPOSSIBLE: {resource['id']})", None
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
    resources.append(RDSClusterParameterGroup)
