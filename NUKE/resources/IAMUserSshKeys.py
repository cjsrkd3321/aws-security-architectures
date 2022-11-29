from . import resources, Config
from ._base import ResourceBase
from .IAMUsers import IAMUser


import boto3


class IAMUserSshKey(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iam_user = IAMUser(default_filter_func=self.filter_func)
            users, err = iam_user.list()
            if err:
                return [], err

            results = []
            for user in users:
                reason, err = iam_user.filter(user)
                if err or reason:
                    continue

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
                            "state": key["Status"],
                        }
                        for key in keys["SSHPublicKeys"]
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
    resources.append(IAMUserSshKey)
