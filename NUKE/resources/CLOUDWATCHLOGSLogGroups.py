from ._base import ResourceBase
from . import resources
from ._utils import convert_dict_to_tags


class CLOUDWATCHLOGSLogGroup(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["logs"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_log_groups").paginate()
            logs = [log for logs in iterator for log in logs["logGroups"]]
            for log in logs:
                log_name = log["logGroupName"]
                log_arn = log["arn"][:-2]  # ...log-group:name:* -> ...log-group:name
                try:
                    tags = self.svc.list_tags_for_resource(resourceArn=log_arn)["tags"]
                except Exception as e:
                    tags = []

                results.append(
                    {
                        "id": log_name,
                        "name": log_name,
                        "tags": convert_dict_to_tags(tags),
                        "create_date": log["creationTime"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_log_group(logGroupName=resource["id"])
            return True, None
        except self.exceptions.ResourceNotFoundException:
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
    resources.append(CLOUDWATCHLOGSLogGroup)
