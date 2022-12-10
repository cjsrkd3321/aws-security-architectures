from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class EFSFilesystem(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("describe_file_systems").paginate()
            fss = [fs for fss in iterator for fs in fss["FileSystems"]]
            for fs in fss:
                results.append(
                    {
                        "id": fs["FileSystemId"],
                        "name": fs.get("Name", ""),
                        "tags": fs["Tags"],
                        "arn": fs["FileSystemArn"],
                        "create_date": fs["CreationTime"],
                        "unique_id": fs.get("registryId"),
                        "state": fs["LifeCycleState"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_file_system(FileSystemId=resource["id"])
            return True, None
        except self.exceptions.FileSystemNotFound:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        if resource["state"].startswith("delet"):
            return f"DEFAULT(IMPOSSIBLE: {resource['state']})", None
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
    resources.append(EFSFilesystem)
