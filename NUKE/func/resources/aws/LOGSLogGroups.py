from botocore.exceptions import ClientError

from resources import resources
from resources.base import ResourceBase
from resources.utils import convert_dict_to_tags


class LOGSLogGroup(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

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
                except self.exceptions.ResourceNotFoundException:
                    tags = []
                except ClientError as e:
                    if e.response["Error"]["Code"] == "AccessDeniedException":
                        continue
                    raise e

                results.append(
                    {
                        "id": log_name,
                        "name": log_name,
                        "tags": convert_dict_to_tags(tags),
                        "create_date": log["creationTime"],
                        "retention_days": log.get("retentionInDays"),
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
    resources.append(LOGSLogGroup)
