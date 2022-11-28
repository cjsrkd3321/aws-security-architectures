from . import resources, Config
from ._base import ResourceBase
from .IAMRoles import IAMRole


import boto3


class IAMRolePolicyAttachment(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iam_role = IAMRole(default_filter_func=self.filter_func)
            roles, err = iam_role.list()
            if err:
                return [], err

            results = []
            for role in roles:
                filtered_role, err = iam_role.filter(role)
                if err or filtered_role:
                    continue

                role_name = role["id"]
                try:
                    attached_policies = self.svc.list_attached_role_policies(
                        RoleName=role_name
                    )
                    if not attached_policies:
                        return [], None
                    results += [
                        {
                            "id": policy["PolicyArn"],
                            "name": policy["PolicyName"],
                            "role_name": role_name,
                            "arn": policy["PolicyArn"],
                        }
                        for policy in attached_policies["AttachedPolicies"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_role_policy(
                    RoleName=resource["role_name"], PolicyArn=resource["id"]
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
    resources.append(IAMRolePolicyAttachment)
