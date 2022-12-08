from resources import resources
from resources.base import ResourceBase
from resources.utils import convert_dict_to_tags


class GRAFANAWorkspace(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["grafana"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_workspaces").paginate()
            wss = [ws for wss in iterator for ws in wss["workspaces"]]
            for ws in wss:
                results.append(
                    {
                        "id": ws["id"],
                        "name": ws["name"],
                        "tags": convert_dict_to_tags(ws["tags"]),
                        "create_date": ws["created"],
                        "last_modified_date": ws["modified"],
                        "description": ws.get("description"),
                        "state": ws["status"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_workspace(workspaceId=resource["id"])
            return True, None
        except self.exceptions.ResourceNotFoundException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["state"] in ["CREATING", "DELETING"]:
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
    resources.append(GRAFANAWorkspace)
