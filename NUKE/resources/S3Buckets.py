from ._base import ResourceBase
from . import resources


cache: dict = {}


class S3Bucket(ResourceBase):
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
            buckets = self.svc.list_buckets()

            buckets = [bucket for bucket in buckets["Buckets"]]
            for bucket in buckets:
                bucket_name = bucket["Name"]

                try:
                    region = self.svc.get_bucket_location(Bucket=bucket_name)[
                        "LocationConstraint"
                    ]
                    region = region if region else "us-east-1"
                    if self.region != region:
                        continue
                except self.exceptions.NoSuchBucket:
                    continue

                try:
                    tags = self.svc.get_bucket_tagging(Bucket=bucket_name)["TagSet"]
                except Exception as e:
                    if e.response.get("Error", {}).get("Code") == "NoSuchTagSet":
                        tags = []
                    else:
                        continue

                results.append(
                    {
                        "id": bucket_name,
                        "name": bucket_name,
                        "tags": tags,
                        "create_date": bucket["CreationDate"],
                    }
                )
            cache[self.svc] = results if has_cache else None
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_bucket(Bucket=resource["id"])
            return True, None
        except self.exceptions.NoSuchBucket:
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
    resources.append(S3Bucket)
