from ._base import ResourceBase
from . import resources, Config
from .IAMGroups import IAMGroup

import boto3


class IAMGroupPolicyAttachment(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iam_group = IAMGroup(
                region=self.region, default_filter_func=self.filter_func
            )
            groups, err = iam_group.list(has_cache=True)
            if err:
                return results, err

            for group in groups:
                reason, err = iam_group.filter(group)
                if err or reason:
                    continue

                group_name = group["id"]
                try:
                    attached_policies = self.svc.list_attached_group_policies(
                        GroupName=group_name
                    )
                    if not attached_policies:
                        return results, None
                    results += [
                        {
                            "id": policy["PolicyArn"],
                            "name": policy["PolicyName"],
                            "group_name": group_name,
                            "arn": policy["PolicyArn"],
                        }
                        for policy in attached_policies["AttachedPolicies"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_group_policy(
                    GroupName=resource["group_name"], PolicyArn=resource["id"]
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
    resources.append(IAMGroupPolicyAttachment)
