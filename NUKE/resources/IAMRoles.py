from ._base import ResourceBase
from . import resources, Config

import boto3


cache = None


class IAMRole(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        global cache
        if cache:
            return cache, None

        try:
            iterator = self.svc.get_paginator("list_roles").paginate()

            results = []
            roles = [role for roles in iterator for role in roles["Roles"]]
            for role in roles:
                role_name = role["RoleName"]

                try:
                    r = self.svc.get_role(RoleName=role_name)["Role"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": role_name,
                        "name": role_name,
                        "path": r["Path"],
                        "tags": r.get("Tags", []),
                        "arn": r["Arn"],
                        "unique_id": r["RoleId"],
                        "create_date": r["CreateDate"],
                        "last_used_date": r["RoleLastUsed"].get("LastUsedDate"),
                        "description": r.get("Description"),
                    }
                )
                cache = results
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_role(RoleName=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
                == 200
            ), None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if not resource:
            return "Invalid resource", None
        if resource["path"].startswith("/aws-service-role/") or resource[
            "path"
        ].startswith("/aws-reserved/"):
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
    resources.append(IAMRole)
