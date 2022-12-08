from resources import resources
from resources.base import ResourceBase


class EC2SecurityGroup(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_security_groups").paginate()
            results += [
                {
                    "id": (sg := security_group)["GroupId"],
                    "name": sg["GroupName"],
                    "tags": sg.get("Tags", []),
                    "description": sg.get("Description"),
                    "vpc_id": sg.get("VpcId"),
                    "ingress": sg["IpPermissions"],
                    "egress": sg["IpPermissionsEgress"],
                }
                for security_groups in iterator
                for security_group in security_groups["SecurityGroups"]
                if security_group["GroupName"] != "default"
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            if len(resource["ingress"]) > 0:
                self.svc.revoke_security_group_ingress(
                    GroupId=resource["id"], IpPermissions=resource["ingress"]
                )
            if len(resource["egress"]) > 0:
                self.svc.revoke_security_group_egress(
                    GroupId=resource["id"], IpPermissions=resource["egress"]
                )

            self.svc.delete_security_group(GroupId=resource["id"])
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
    resources.append(EC2SecurityGroup)
