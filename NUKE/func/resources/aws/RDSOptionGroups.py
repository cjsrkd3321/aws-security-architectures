from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class RDSOptionGroup(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("describe_option_groups").paginate()
            option_groups = [
                og
                for option_groups in iterator
                for og in option_groups["OptionGroupsList"]
            ]
            for option_group in option_groups:
                name = option_group["OptionGroupName"]
                arn = option_group["OptionGroupArn"]
                tags = self.svc.list_tags_for_resource(ResourceName=arn)["TagList"]
                results.append(
                    {
                        "id": name,
                        "name": name,
                        "tags": tags,
                        "description": option_group.get("OptionGroupDescription", ""),
                        "arn": arn,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_option_group(OptionGroupName=resource["id"])
            return True, None
        except self.exceptions.OptionGroupNotFoundFault:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["id"].startswith("default:"):
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
    resources.append(RDSOptionGroup)
