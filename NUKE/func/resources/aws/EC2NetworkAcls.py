from resources import resources
from resources.base import ResourceBase
from resources.utils import get_name_from_tags


class EC2NetworkAcl(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_network_acls").paginate()
            acls = [acl for acls in iterator for acl in acls["NetworkAcls"]]
            for acl in acls:
                results.append(
                    {
                        "id": acl["NetworkAclId"],
                        "tags": (tags := acl.get("Tags", [])),
                        "name": get_name_from_tags(tags),
                        "is_default": acl["IsDefault"],
                        "owner_id": acl["OwnerId"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_network_acl(NetworkAclId=resource["id"])
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["is_default"]:
            return f"DEFAULT(IMPOSSIBLE: {resource['is_default']})", None
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
    resources.append(EC2NetworkAcl)
