from resources import resources
from resources.base import ResourceBase

import time


class SNSTopic(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["sns"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_topics").paginate()
            topics = [topic for topics in iterator for topic in topics["Topics"]]
            for topic in topics:
                arn = topic["TopicArn"]
                try:
                    tags = self.svc.list_tags_for_resource(ResourceArn=arn)["Tags"]
                except self.exceptions.ResourceNotFoundException:
                    continue
                except self.exceptions.ConcurrentAccessException:
                    time.sleep(0.1)

                try:
                    attrs = self.svc.get_topic_attributes(TopicArn=arn)["Attributes"]
                except self.exceptions.NotFoundException:
                    pass

                results.append(
                    {
                        "id": arn,
                        "name": attrs["DisplayName"],
                        "tags": tags,
                        "arn": arn,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_topic(TopicArn=resource["id"])
            return True, None
        except self.exceptions.NotFoundException:
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
    resources.append(SNSTopic)
