from ._base import ResourceBase
from . import resources, Config

import boto3


class IAMLoginProfile(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("list_users").paginate()

            results = []
            users = [user for users in iterator for user in users["Users"]]
            for user in users:
                user_name = user["UserName"]

                try:
                    p = self.svc.get_login_profile(UserName=user_name)["LoginProfile"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": user_name,
                        "name": user_name,
                        "create_date": p["CreateDate"],
                        "password_reset_required": p["PasswordResetRequired"],
                    }
                )
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_login_profile(UserName=resource["id"])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
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
    resources.append(IAMLoginProfile)
