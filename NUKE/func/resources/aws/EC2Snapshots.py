from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import get_name_from_tags


class EC2Snapshot(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("describe_snapshots").paginate(
                OwnerIds=["self"]
            )
            results += [
                {
                    "id": snapshot["SnapshotId"],
                    "tags": (tags := snapshot.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "create_date": snapshot["StartTime"],
                    "unique_id": snapshot["SnapshotId"],
                    "description": snapshot.get("Description"),
                    "state": snapshot["State"],
                    "is_encrypted": snapshot.get("Encrypted"),
                }
                for snapshots in iterator
                for snapshot in snapshots["Snapshots"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_snapshot(SnapshotId=resource["id"])
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
    resources.append(EC2Snapshot)
