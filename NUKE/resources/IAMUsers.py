from ._base import ResourceBase
from . import resources, Config

import boto3


class IAMUser(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iterator = self.svc.get_paginator("list_users").paginate()
            return [
                {
                    "id": user["UserName"],
                    "tags": user.get("Tags"),
                    "name": user["UserName"],
                    "create_date": user["CreateDate"],
                }
                for users in iterator
                for user in users["Users"]
            ], None
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
    resources.append(IAMUser)
