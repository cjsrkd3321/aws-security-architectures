from ._base import ResourceBase
from . import resources, Config

import boto3


cache = None


class IAMGroup(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self, has_cache=False):
        global cache
        if cache and has_cache:
            return cache, None

        try:
            iterator = self.svc.get_paginator("list_groups").paginate(Scope="Local")

            results = []
            groups = [group for groups in iterator for group in groups["Groups"]]
            for group in groups:
                group_name = group["GroupName"]

                results.append(
                    {
                        "id": group_name,
                        "name": group_name,
                        "path": group["Path"],
                        "arn": group["Arn"],
                        "unique_id": group["GroupId"],
                        "create_date": group["CreateDate"],
                    }
                )
                cache = results if has_cache else None
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_group(GroupName=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
                == 200
            ), None
        except self.exceptions.NoSuchEntityException:
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
    resources.append(IAMGroup)
