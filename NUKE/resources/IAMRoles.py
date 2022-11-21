from ._base import ResourceBase
from . import resources, Config

import boto3


class IAMRole(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iterator = self.svc.get_paginator("list_roles").paginate()
            if not iterator:
                return []

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
                        "tags": r.get("Tags"),
                    }
                )
            return results
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_role(RoleName=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
                == 200
            )
        except self.exceptions.NoSuchEntityException:
            return True
        except Exception as e:
            return e

    def filter(self, resources, filter_func=None):
        if not resources:
            return []
        filtered_resources = [
            r
            for r in resources
            if not r["path"].startswith("/aws-service-role/")
            and not r["path"].startswith("/aws-reserved/")
        ]
        if filter_func:
            filtered_resources = filter_func(filtered_resources)
        return filtered_resources

    def properties(self):
        pass


if __name__ == "__main__":
    role = IAMRole()
    print(role.filter(role.list()))
else:
    resources.append(IAMRole)
