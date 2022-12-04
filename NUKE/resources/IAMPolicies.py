from ._base import ResourceBase
from . import resources


cache: dict = {}


class IAMPolicy(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self, has_cache=False):
        global cache
        if cache.get(self.svc) and has_cache:
            return cache[self.svc], None

        results = []
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

    def remove(self, resource):
        try:
            return (
                self.svc.delete_policy(PolicyArn=resource["id"])["ResponseMetadata"][
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
    resources.append(IAMPolicy)
