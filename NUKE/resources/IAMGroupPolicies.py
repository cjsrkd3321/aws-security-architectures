from ._base import ResourceBase
from . import resources, Config
from .IAMGroups import IAMGroup

import boto3


cache = None


class IAMGroupPolicy(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iam_group = IAMGroup(default_filter_func=self.filter_func)
            groups, err = iam_group.list(has_cache=True)
            if err:
                return [], err

            results = []
            for group in groups:
                reason, err = iam_group.filter(group)
                if err or reason:
                    continue

                group_name = group["id"]
                try:
                    policies = self.svc.list_group_policies(GroupName=group_name)
                    if not policies:
                        return [], None
                    results += [
                        {
                            "id": policy,
                            "name": policy,
                            "group_name": group_name,
                        }
                        for policy in policies["PolicyNames"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_group_policy(
                    GroupName=resource["id"], PolicyArn=resource["group_name"]
                )["ResponseMetadata"]["HTTPStatusCode"]
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
    resources.append(IAMGroupPolicy)
