from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class RDSSubnet(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("describe_db_subnet_groups").paginate()
            subnets = [s for subnets in iterator for s in subnets["DBSubnetGroups"]]
            for subnet in subnets:
                name = subnet["DBSubnetGroupName"]
                arn = subnet["DBSubnetGroupArn"]
                tags = self.svc.list_tags_for_resource(ResourceName=arn)["TagList"]
                results.append(
                    {
                        "id": name,
                        "name": name,
                        "tags": tags,
                        "description": subnet.get("DBSubnetGroupDescription"),
                        "arn": arn,
                        "state": subnet["SubnetGroupStatus"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_db_subnet_group(DBSubnetGroupName=resource["id"])
            return True, None
        except self.exceptions.DBSubnetGroupNotFoundFault:
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
    resources.append(RDSSubnet)
