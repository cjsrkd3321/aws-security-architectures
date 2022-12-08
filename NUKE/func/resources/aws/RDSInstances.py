from resources import resources
from resources.base import ResourceBase


class RDSInstance(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_db_instances").paginate()
            instances = [i for instances in iterator for i in instances["DBInstances"]]
            for instance in instances:
                results.append(
                    {
                        "id": instance["DBInstanceIdentifier"],
                        "name": instance["DBName"],
                        "tags": instance["TagList"],
                        "state": instance["DBInstanceStatus"],
                        "unique_id": instance.get("DBSystemId"),
                        "is_public_access": instance.get("PubliclyAccessible"),
                        "create_date": instance.get("InstanceCreateTime"),
                        "arn": instance["DBInstanceArn"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_db_instance(
                DBInstanceIdentifier=resource["id"], SkipFinalSnapshot=True
            )
            return True, None
        except self.exceptions.DBInstanceNotFoundFault:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["state"] == "deleting":
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
    resources.append(RDSInstance)
