from resources import resources
from resources.base import ResourceBase


class RDSEventSubscription(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["rds"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_event_subscriptions").paginate()
            subs = [s for subs in iterator for s in subs["EventSubscriptionsList"]]
            for sub in subs:
                arn = sub["EventSubscriptionArn"]
                tags = self.svc.list_tags_for_resource(ResourceName=arn)["TagList"]
                results.append(
                    {
                        "id": sub["CustSubscriptionId"],
                        "name": sub["CustSubscriptionId"],
                        "tags": tags,
                        "state": sub["Status"],
                        "create_date": sub.get("SubscriptionCreationTime"),
                        "arn": arn,
                        "is_enabled": sub["Enabled"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_event_subscription(SubscriptionName=resource["id"])
            return True, None
        except self.exceptions.SubscriptionNotFoundFault:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["state"] in ["deleting", "topic-not-exist"]:
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
    resources.append(RDSEventSubscription)
