from . import resources, Config
from ._base import ResourceBase
from .IAMUsers import IAMUser


import boto3


class IAMMfaDevice(ResourceBase):
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
                user, err = iam_user.filter(user)
                if err or user:
                    continue

                user_name = user["id"]
                try:
                    devices = self.svc.list_mfa_devices(UserName=user_name)
                    if not devices:
                        return [], None
                    results += [
                        {
                            "id": device["SerialNumber"],
                            "name": device["SerialNumber"],
                            "user_name": user_name,
                        }
                        for device in devices["MFADevices"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.deactivate_mfa_device(
                    UserName=resource["user_name"], SerialNumber=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
            ) == 200 and (
                self.svc.delete_virtual_mfa_device(SerialNumber=resource["id"])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
            ) == 200, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["id"].endswith("/root-account-mfa-device"):
            return "default rule", None
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
    resources.append(IAMMfaDevice)
