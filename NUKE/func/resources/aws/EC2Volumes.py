from resources import resources
from resources.base import ResourceBase
from resources.utils import get_name_from_tags


class EC2Volume(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_volumes").paginate()
            results += [
                {
                    "id": volume["VolumeId"],
                    "tags": (tags := volume.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "create_date": volume["CreateTime"],
                    "unique_id": volume["VolumeId"],
                    "state": volume["State"],
                    "is_encrypted": volume.get("Encrypted"),
                    "attachments": volume["Attachments"],
                }
                for volumes in iterator
                for volume in volumes["Volumes"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_volume(VolumeId=resource["id"])
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        for a in resource["attachments"]:
            if a["DeleteOnTermination"]:
                return "DEFAULT(INSTANCE DEPENDENCY)", None
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
    resources.append(EC2Volume)
