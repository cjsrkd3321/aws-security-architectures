from . import resources, Config
from ._base import ResourceBase
from .IAMRoles import IAMRole


import boto3


class IAMRolePolicy(ResourceBase):
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
            filtered_roles, err = iam_role.filter(roles)
            if err:
                return [], err

            results = []
            for role in filtered_roles:
                role_name = role["id"]
                try:
                    policies = self.svc.list_role_policies(RoleName=role_name)
                    if not policies:
                        return [], None
                    results += [
                        {
                            "id": policy,
                            "name": policy,
                            "role_name": role_name,
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
                self.svc.delete_role_policy(
                    RoleName=resource["role_name"], PolicyName=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            ), None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resources, *filters):
        if not resources:
            return [], None
        filtered_resources = resources
        if self.filter_func:
            try:
                filtered_resources = self.filter_func(filtered_resources)
            except Exception as e:
                return [], e
        for filter in filters:
            filtered_resources = filter(filtered_resources)
        return filtered_resources, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(IAMRolePolicy)