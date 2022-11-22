from . import resources, Config
from ._base import ResourceBase
from ._utils import filter_func
from .IAMUsers import IAMUser


import boto3


class IAMUserAccessKey(ResourceBase):
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
                    access_keys = self.svc.list_access_keys(UserName=user_name)
                    if not access_keys:
                        return [], None
                    results += [
                        {
                            "id": access_key["AccessKeyId"],
                            "name": access_key["AccessKeyId"],
                            "user_name": user_name,
                            "tags": [],
                        }
                        for access_key in access_keys["AccessKeyMetadata"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_access_key(
                    UserName=resource["user_name"], AccessKeyId=resource["id"]
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


if __name__ == "__main__":
    role = IAMUserAccessKey()
    print(role.filter(role.list()))
else:
    resources.append(IAMUserAccessKey)
    if IAMUser in resources:
        resources.remove(IAMUser)
