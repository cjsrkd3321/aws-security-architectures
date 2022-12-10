from resources import resources
from resources.base import ResourceBase


class ELBv2TargetGroup(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_target_groups").paginate()
            tgs = [tg for tgs in iterator for tg in tgs["TargetGroups"]]
            for tg in tgs:
                arn = tg["TargetGroupArn"]
                try:
                    tags = self.svc.describe_tags(ResourceArns=[arn])["TagDescriptions"]
                except self.exceptions.LoadBalancerNotFoundException:
                    continue
                results.append(
                    {
                        "id": arn,
                        "name": tg["TargetGroupName"],
                        "tags": tags[0]["Tags"],
                        "type": tg["TargetType"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_target_group(TargetGroupArn=resource["id"])
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
    resources.append(ELBv2TargetGroup)
