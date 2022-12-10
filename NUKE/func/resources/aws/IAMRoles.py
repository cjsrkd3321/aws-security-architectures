from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


cache: dict = {}


class IAMRole(ResourceBase):
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
            iterator = self.svc.get_paginator("list_roles").paginate()

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
            cache[self.svc] = results if has_cache else None
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_role(RoleName=resource["id"])
            return True, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if (rp := resource["path"]).startswith("/aws-service-role/") or rp.startswith(
            "/aws-reserved/"
        ):
            return f"DEFAULT(IMPOSSIBLE {resource['path']})", None
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
