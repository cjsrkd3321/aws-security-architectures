from ._base import ResourceBase
from . import resources, Config

import boto3


cache = None


class IAMUser(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self, has_cache=False):
        global cache
        if cache and has_cache:
            return cache, None

        try:
            iterator = self.svc.get_paginator("list_users").paginate()

            results = []
            users = [user for users in iterator for user in users["Users"]]
            for user in users:
                user_name = user["UserName"]

                try:
                    u = self.svc.get_user(UserName=user_name)["User"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": user_name,
                        "tags": u.get("Tags", []),
                        "name": user_name,
                        "create_date": user["CreateDate"],
                        "last_used_date": user.get("PasswordLastUsed"),
                        "unique_id": user["UserId"],
                        "path": user["Path"],
                        "arn": user["Arn"],
                        "permissions_boundary": user.get("PermissionsBoundary"),
                    }
                )
            cache = results if has_cache else None
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_user(UserName=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
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
    resources.append(IAMUser)
