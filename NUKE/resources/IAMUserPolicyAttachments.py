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
            users, err = iam_user.list()
            if err:
                return [], err
            filtered_users, err = iam_user.filter(users, filter_func)
            if err:
                return [], err

            results = []
            for user in filtered_users:
                user_name = user["id"]
                try:
                    attached_policies = self.svc.list_attached_user_policies(
                        UserName=user_name
                    )
                    if not attached_policies:
                        return [], None
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
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_user_policy(
                    UserName=resource["user_name"], PolicyArn=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            ), None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resources, filter_func=None):
        if not resources:
            return [], None
        filtered_resources = resources
        if filter_func:
            try:
                filtered_resources = filter_func(filtered_resources)
            except Exception as e:
                return [], e
        return filtered_resources, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(IAMUserPolicyAttachment)