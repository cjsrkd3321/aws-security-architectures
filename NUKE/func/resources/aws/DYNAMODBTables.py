from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class DYNAMODBTable(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            iterator = self.svc.get_paginator("list_tables").paginate()
            tables = [tb for tables in iterator for tb in tables.get("TableNames", [])]
            for table in tables:
                table_name = table

                try:
                    tb = self.svc.describe_table(TableName=table_name)["Table"]
                    iterator = self.svc.get_paginator("list_tags_of_resource").paginate(
                        ResourceArn=tb["TableArn"]
                    )
                    tags = [tag for tags in iterator for tag in tags["Tags"]]
                except self.svc.ResourceNotFoundException:
                    continue

                results.append(
                    {
                        "id": table_name,
                        "name": table_name,
                        "tags": tags,
                        "create_date": tb["CreationDateTime"],
                        "arn": tb["TableArn"],
                        "unique_id": tb["TableId"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_table(TableName=resource["id"])
            return True, None
        except self.svc.ResourceNotFoundException:
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
    resources.append(DYNAMODBTable)
