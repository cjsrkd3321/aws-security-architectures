from botocore.exceptions import ClientError

from resources import resources
from resources.base import ResourceBase
from resources.utils import convert_dict_to_tags


class SQSQueue(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_queues").paginate()
            queues = [q for queues in iterator for q in queues.get("QueueUrls", [])]
            for queue in queues:
                queue_name = queue.split("/")[-1]

                try:
                    tags = self.svc.list_queue_tags(QueueUrl=queue)["Tags"]
                    attrs = self.svc.get_queue_attributes(
                        QueueUrl=queue, AttributeNames=["All"]
                    )["Attributes"]
                except ClientError as e:
                    if e.response["Error"]["Code"] in [
                        "AccessDeniedException",
                        "AWS.SimpleQueueService.NonExistentQueue",
                    ]:
                        continue
                    raise e

                results.append(
                    {
                        "id": queue,
                        "name": queue_name,
                        "tags": convert_dict_to_tags(tags),
                        "create_date": attrs["CreatedTimestamp"],
                        "last_modified_date": attrs["LastModifiedTimestamp"],
                        "arn": attrs["QueueArn"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_queue(QueueUrl=resource["id"])
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
    resources.append(SQSQueue)
