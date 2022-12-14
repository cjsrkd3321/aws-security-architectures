from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import convert_dict_to_tags


class LAMBDAFunction(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("list_functions").paginate()
            functions = [f for functions in iterator for f in functions["Functions"]]
            for f in functions:
                function_name = f["FunctionName"]
                function_arn = f["FunctionArn"]

                try:
                    tags = self.svc.list_tags(Resource=function_arn)["Tags"]
                except self.exceptions.ResourceNotFoundException:
                    continue

                results.append(
                    {
                        "id": function_name,
                        "name": function_name,
                        "tags": convert_dict_to_tags(tags),
                        "arn": function_arn,
                        "description": f.get("Description"),
                        "state": f.get("State"),
                        "last_modified_date": f["LastModified"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_function(FunctionName=resource["id"])
            return True, None
        except self.exceptions.ResourceNotFoundException:
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
    resources.append(LAMBDAFunction)
