from ._base import ResourceBase
from ._utils import get_name_from_tags
from . import resources


class EC2Instance(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess["ec2"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_instances").paginate()
            results += [
                {
                    "id": (i := instance)["InstanceId"],
                    "tags": (tags := i.get("Tags", [])),
                    "name": get_name_from_tags(tags),
                    "state": i["State"]["Name"],
                    "type": i["InstanceType"],
                    "create_date": i["LaunchTime"],
                    "architecture": i.get("Architecture"),
                    "instance_profile": i.get("IamInstanceProfile"),
                    "lifecycle": i.get("InstanceLifecycle"),
                    "security_groups": i.get("SecurityGroups"),
                    "cpu_core_count": i["CpuOptions"]["CoreCount"],
                    "platform": i.get("Platform"),
                }
                for instances in iterator
                for reservations in instances["Reservations"]
                for instance in reservations["Instances"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.terminate_instances(InstanceIds=[resource["id"]])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["state"] in ["shutting-down", "terminated"]:
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
    resources.append(EC2Instance)
