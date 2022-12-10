from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


cache: dict = {}


class IAMPolicy(ResourceBase):
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
            iterator = self.svc.get_paginator("list_policies").paginate(Scope="Local")
            policies = [
                policy for policies in iterator for policy in policies["Policies"]
            ]
            for policy in policies:
                policy_arn = policy["Arn"]

                try:
                    p = self.svc.get_policy(PolicyArn=policy_arn)["Policy"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": policy_arn,
                        "name": p["PolicyName"],
                        "path": p["Path"],
                        "tags": p.get("Tags", []),
                        "arn": policy_arn,
                        "unique_id": p["PolicyId"],
                        "create_date": p["CreateDate"],
                        "update_date": p["UpdateDate"],
                        "description": p.get("Description"),
                        "attachment_count": p["AttachmentCount"],
                        "is_attachable": p["IsAttachable"],
                    }
                )
            cache[self.svc] = results if has_cache else None
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_policy(PolicyArn=resource["id"])
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
    resources.append(IAMPolicy)
