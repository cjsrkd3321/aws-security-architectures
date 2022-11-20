from ._base import ResourceBase
from . import resources, Config

import boto3


class IAMUser(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            paginator = self.svc.get_paginator("list_users")
            iterator = paginator.paginate()
            if not iterator:
                return []
            return [
                {
                    "id": user["UserName"],
                    "tags": user.get("Tags"),
                    "name": user["UserName"],
                    "create_date": user["CreateDate"],
                }
                for users in iterator
                for user in users["Users"]
            ]
        except Exception as e:
            return e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_user(UserName=resource["id"])["ResponseMetadata"][
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
        filtered_resources = resources
        if filter_func:
            filtered_resources = filter_func(filtered_resources)
        return filtered_resources

    def properties(self):
        pass


if __name__ == "__main__":
    user = IAMUser()
    print(user.filter(user.list()))
else:
    resources.append(IAMUser)
