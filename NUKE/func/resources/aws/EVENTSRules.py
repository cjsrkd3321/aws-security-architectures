from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class EVENTSRule(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("list_rules").paginate()
            rules = [rule for rules in iterator for rule in rules["Rules"]]
            for rule in rules:
                name = rule["Name"]
                arn = rule["Arn"]
                try:
                    tags = self.svc.list_tags_for_resource(ResourceARN=arn)["Tags"]
                except self.exceptions.ResourceNotFoundException:
                    continue

                try:
                    targets = self.svc.list_targets_by_rule(Rule=name)["Targets"]
                    target_ids = [target["Id"] for target in targets]
                except self.exceptions.ResourceNotFoundException:
                    target_ids = []

                results.append(
                    {
                        "id": name,
                        "name": name,
                        "tags": tags,
                        "state": rule["State"],
                        "description": rule.get("Description", ""),
                        "event_bus_name": rule["EventBusName"],
                        "target_ids": target_ids,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            if len(resource["target_ids"]) > 0:
                self.svc.remove_targets(
                    Rule=resource["id"], Ids=resource["target_ids"], Force=True
                )
        except self.exceptions.ResourceNotFoundException:
            pass

        try:
            self.svc.delete_rule(Name=resource["id"], Force=True)
            return True, None
        except self.exceptions.ResourceNotFoundException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
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
    resources.append(EVENTSRule)
