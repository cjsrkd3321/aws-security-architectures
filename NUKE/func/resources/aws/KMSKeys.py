from botocore.exceptions import ClientError

from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import delete_tag_prefix


cache: dict = {}


class KMSKey(ResourceBase):
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
            iterator = self.svc.get_paginator("list_keys").paginate()
            keys = [key for keys in iterator for key in keys["Keys"]]
            for key in keys:
                key_id = key["KeyId"]

                try:
                    try:
                        key_meta = self.svc.describe_key(KeyId=key_id)["KeyMetadata"]
                        tags = self.svc.list_resource_tags(KeyId=key_id)["Tags"]
                    except self.exceptions.NotFoundException:
                        continue

                    try:
                        aliases = self.svc.list_aliases(KeyId=key_id)["Aliases"]
                        alias = aliases[0] if aliases else {}
                    except self.exceptions.NotFoundException:
                        alias = {}
                except ClientError as e:
                    if e.response["Error"]["Code"] == "AccessDeniedException":
                        continue
                    raise e

                results.append(
                    {
                        "id": key_id,
                        "name": alias.get("AliasName"),
                        "tags": delete_tag_prefix(tags),
                        "create_date": key_meta["CreationDate"],
                        "valid_date": key_meta.get("ValidTo"),
                        "delete_date": key_meta.get("DeletionDate"),
                        "arn": key["KeyArn"],
                        "manager": key_meta["KeyManager"],
                        "description": key_meta.get("Description"),
                        "state": key_meta["KeyState"],
                        "is_enabled": key_meta["Enabled"],
                    }
                )
            cache[self.svc] = results if has_cache else None
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.schedule_key_deletion(KeyId=resource["id"], PendingWindowInDays=7)
            return True, None
        except self.exceptions.NoSuchBucket:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["state"] == "PendingDeletion":
            return f"DEFAULT(IMPOSSIBLE: {resource['state']})", None
        if resource["manager"] == "AWS":
            return f"DEFAULT(IMPOSSIBLE: {resource['manager']})", None
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
    resources.append(KMSKey)
