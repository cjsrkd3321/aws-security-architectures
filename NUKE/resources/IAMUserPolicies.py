from . import resources, Config
from ._base import ResourceBase
from ._utils import filter_func
from .IAMUsers import IAMUser


import boto3


class IAMUserPolicy(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iam_user = IAMUser()
            filtered_users = iam_user.filter(iam_user.list(), filter_func)

            results = []
            for user in filtered_users:
                user_name = user["id"]
                try:
                    policies = self.svc.list_user_policies(UserName=user_name)
                    if not policies:
                        return []
                    results += [
                        {
                            "id": policy,
                            "name": policy,
                            "user_name": user_name,
                            "tags": [],
                        }
                        for policy in policies["PolicyNames"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_user_policy(
                    UserName=resource["user_name"], PolicyName=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            )
        except self.exceptions.NoSuchEntityException:
            return True
        except Exception as e:
            return e

    def filter(self, resources, filter_func=None):
        if not resources:
            return []
        filtered_resources = resources
        if filter_func:
            filtered_resources = filter_func(filtered_resources)
        return filtered_resources

    def properties(self):
        pass


if __name__ == "__main__":
    role = IAMUserPolicy()
    print(role.filter(role.list()))
else:
    resources.append(IAMUserPolicy)
    if IAMUser in resources:
        resources.remove(IAMUser)
