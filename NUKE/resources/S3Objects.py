from ._base import ResourceBase
from . import resources


cache: dict = {}


class S3Object(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["s3"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self, has_cache=False):
        global cache
        if cache.get(self.svc) and has_cache:
            return cache[self.svc], None

        results = []
        try:
            from .S3Buckets import S3Bucket

            s3_bucket = S3Bucket(self.svc, self.region, self.filter_func)
            buckets, err = s3_bucket.list(has_cache=True)
            if err:
                return results, err

            for bucket in buckets:
                reason, err = s3_bucket.filter(bucket)
                if err or reason:
                    continue

                bucket_name = bucket["id"]
                iterator = self.svc.get_paginator("list_object_versions").paginate(
                    Bucket=bucket_name
                )
                for objects in iterator:
                    for version in objects.get("Versions", []):
                        results.append(
                            {
                                "id": version["Key"],
                                "name": version["Key"],
                                "version_id": version["VersionId"],
                                "last_modified_date": version["LastModified"],
                                "bucket": bucket_name,
                            }
                        )
                    for delete_marker in objects.get("DeleteMarkers", []):
                        results.append(
                            {
                                "id": delete_marker["Key"],
                                "name": version["Key"],
                                "version_id": delete_marker["VersionId"],
                                "last_modified_date": delete_marker["LastModified"],
                                "bucket": bucket_name,
                            }
                        )
            cache[self.svc] = results if has_cache else None
            return results, None
        except (self.exceptions.NoSuchBucket, self.exceptions.NoSuchKey):
            return True, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_object(
                Bucket=resource["bucket"],
                Key=resource["id"],
                VersionId=resource["version_id"],
            )
            return True, None
        except (self.exceptions.NoSuchBucket, self.exceptions.NoSuchKey):
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
    resources.append(S3Object)
