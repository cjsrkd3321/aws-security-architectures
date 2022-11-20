from . import resources, Config
from ._base import ResourceBase
from ._utils import filter_func
from .IAMUsers import IAMUser


import boto3


class IAMUserPolicyAttachment(ResourceBase):
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
                    attached_policies = self.svc.list_attached_user_policies(
                        UserName=user_name
                    )
                    if not attached_policies:
                        return []
                    results += [
                        {
                            "id": policy["PolicyArn"],
                            "name": policy["PolicyName"],
                            "user_name": user_name,
                            "tags": [],
                        }
                        for policy in attached_policies["AttachedPolicies"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_user_policy(
                    UserName=resource["user_name"], PolicyArn=resource["id"]
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
    role = IAMUserPolicyAttachment()
    print(role.filter(role.list()))
else:
    resources.append(IAMUserPolicyAttachment)
    if IAMUser in resources:
        resources.remove(IAMUser)
