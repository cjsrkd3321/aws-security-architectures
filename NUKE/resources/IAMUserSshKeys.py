from . import resources, Config
from ._base import ResourceBase
from ._utils import filter_func
from .IAMUsers import IAMUser


import boto3


class IAMUserSshKey(ResourceBase):
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
                    keys = self.svc.list_ssh_public_keys(UserName=user_name)
                    if not keys:
                        return [], None
                    results += [
                        {
                            "id": key["SSHPublicKeyId"],
                            "name": key["SSHPublicKeyId"],
                            "user_name": user_name,
                            "create_date": key["UploadDate"],
                            "tags": [],
                        }
                        for key in keys["MFADevices"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_ssh_public_key(
                    UserName=resource["user_name"], SSHPublicKeyId=resource["id"]
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
    role = IAMUserSshKey()
    print(role.filter(role.list()))
else:
    resources.append(IAMUserSshKey)
    if IAMUser in resources:
        resources.remove(IAMUser)
