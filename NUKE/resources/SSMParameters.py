from ._base import ResourceBase
from . import resources


class SSMParameter(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["ssm"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_parameters").paginate()
            params = [p for params in iterator for p in params["Parameters"]]
            for param in params:
                param_name = param["Name"]
                try:
                    tags = self.svc.list_tags_for_resource(
                        ResourceType="Parameter", ResourceId=param_name
                    )["TagList"]
                except Exception:
                    continue

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

    def remove(self, resource):
        try:
            self.svc.delete_parameter(Name=resource["id"])
            return True, None
        except self.exceptions.ParameterNotFound:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
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
