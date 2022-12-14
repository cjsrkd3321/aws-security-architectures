from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


cache: dict = {}


class IAMUser(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self, has_cache=False) -> ListResults:
        global cache
        if cache.get(self.svc) and has_cache:
            return cache[self.svc], None

        results: list = []
        try:
            iterator = self.svc.get_paginator("list_users").paginate()
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
            cache[self.svc] = results if has_cache else None
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_user(UserName=resource["id"])
            return True, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
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
