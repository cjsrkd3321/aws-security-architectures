from botocore.exceptions import ClientError

from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class SSMParameter(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("describe_parameters").paginate()
            params = [p for params in iterator for p in params["Parameters"]]
            for param in params:
                param_name = param["Name"]
                try:
                    tags = self.svc.list_tags_for_resource(
                        ResourceType="Parameter", ResourceId=param_name
                    )["TagList"]
                except ClientError as e:
                    if e.response["Error"]["Code"] == "AccessDeniedException":
                        continue
                    raise e

                results.append(
                    {
                        "id": param_name,
                        "name": param_name,
                        "type": param["Type"],
                        "tags": tags,
                        "description": param.get("Description"),
                        "last_modified_user": param.get("LastModifiedUser"),
                        "last_modified_date": param.get("LastModifiedDate"),
                        "last_used_date": param.get("LastAccessedDate"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_parameter(Name=resource["id"])
            return True, None
        except self.exceptions.ParameterNotFound:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
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
    resources.append(SSMParameter)
