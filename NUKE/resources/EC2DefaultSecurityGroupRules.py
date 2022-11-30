from ._base import ResourceBase
from . import resources, Config

import boto3


class EC2DefaultSecurityGroupRule(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("describe_security_groups").paginate(
                Filters=[{"Name": "group-name", "Values": ["default"]}]
            )
            group_ids = [
                security_group["GroupId"]
                for security_groups in iterator
                for security_group in security_groups["SecurityGroups"]
            ]

            iterator = self.svc.get_paginator("describe_security_group_rules").paginate(
                Filters=[{"Name": "group-id", "Values": group_ids}]
            )
            return [
                {
                    "id": (sgr := security_group_rule)["SecurityGroupRuleId"],
                    "name": "default",
                    "group_id": sgr["GroupId"],
                    "is_egress": sgr["IsEgress"],
                    "description": sgr.get("Description"),
                    "unique_id": sgr["SecurityGroupRuleId"],
                }
                for security_group_rules in iterator
                for security_group_rule in security_group_rules["SecurityGroupRules"]
            ], None
        except Exception as e:
            return [], e

    def remove(self, resource):
        res = False
        try:
            if resource["is_egress"]:
                res = self.svc.revoke_security_group_egress(
                    GroupId=resource["group_id"], SecurityGroupRuleIds=[resource["id"]]
                )["Return"]
            else:
                res = self.svc.revoke_security_group_ingress(
                    GroupId=resource["group_id"], SecurityGroupRuleIds=[resource["id"]]
                )["Return"]
            return res, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        return False, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(EC2DefaultSecurityGroupRule)
