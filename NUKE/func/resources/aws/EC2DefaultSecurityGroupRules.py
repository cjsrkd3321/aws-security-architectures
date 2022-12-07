from resources import resources
from resources.base import ResourceBase


class EC2DefaultSecurityGroupRule(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["ec2"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
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
            results += [
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
            ]
            return results, None
        except Exception as e:
            return results, e

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

    def filter(self, _, *__):
        return False, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(EC2DefaultSecurityGroupRule)
