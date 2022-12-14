from concurrent import futures
from botocore.exceptions import ClientError

from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


cache: dict = {}
MAX_WORKERS = 16


def delete_objs(svc, bucket, objects):
    if len(objects) == 0:
        return True, None
    try:
        svc.delete_objects(
            Bucket=bucket,
            Delete={"Objects": objects},
        )
    except Exception as e:
        return False, e
    return True, None


class S3Bucket(ResourceBase):
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
            buckets = self.svc.list_buckets()

            buckets = [bucket for bucket in buckets["Buckets"]]
            for bucket in buckets:
                name = bucket["Name"]

                try:
                    region = self.svc.get_bucket_location(Bucket=name)[
                        "LocationConstraint"
                    ]
                    region = region if region else "us-east-1"
                    if self.svc._client_config.region_name != region:
                        continue
                    tags = self.svc.get_bucket_tagging(Bucket=name).get("TagSet", [])
                except self.exceptions.NoSuchBucket:
                    continue
                except ClientError as e:
                    code = e.response.get("Error", {}).get("Code", "")
                    if code.startswith("AccessDenied"):
                        continue
                    elif code == "NoSuchTagSet":
                        tags = []

                results.append(
                    {
                        "id": name,
                        "name": name,
                        "tags": tags,
                        "create_date": bucket["CreationDate"],
                    }
                )
            cache[self.svc] = results if has_cache else None
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        from .S3Objects import S3Object

        s3_object = S3Object(self.svc, self.filter_func)
        objects, err = s3_object.list(has_cache=True)
        if err:
            return False, err

        try:
            bucket = resource["id"]
            threads = []
            if len(objects) > 0:
                pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

                obj_count, objs = 0, []
                for obj in objects:
                    obj_count += 1
                    objs.append({"Key": obj["id"], "VersionId": obj["version_id"]})

                    if obj_count == 1000:
                        threads.append(pool.submit(delete_objs, self.svc, bucket, objs))
                        obj_count, objs = 0, []
                if obj_count > 0:
                    threads.append(pool.submit(delete_objs, self.svc, bucket, objs))
                    obj_count, objs = 0, []
            for future in futures.as_completed(threads):
                is_succeeded, err = future.result()
                if err or not is_succeeded:
                    return False, err
        except Exception as e:
            return False, e

        try:
            self.svc.delete_bucket(Bucket=bucket)
            return True, None
        except self.exceptions.NoSuchBucket:
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
    resources.append(S3Bucket)
