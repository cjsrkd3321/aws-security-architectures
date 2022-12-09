from resources import resources
from resources.base import ResourceBase


class ECRRepository(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_repositories").paginate()
            repos = [repo for repos in iterator for repo in repos["repositories"]]
            for repo in repos:
                arn = repo["repositoryArn"]
                try:
                    tags = self.svc.list_tags_for_resource(resourceArn=arn)["tags"]
                except self.exceptions.RepositoryNotFoundException:
                    continue
                results.append(
                    {
                        "id": repo["repositoryName"],
                        "name": repo["repositoryName"],
                        "tags": tags,
                        "arn": arn,
                        "create_date": repo["createdAt"],
                        "unique_id": repo.get("registryId"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_repository(repositoryName=resource["id"], force=True)
            return True, None
        except self.exceptions.RepositoryNotFoundException:
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
    resources.append(ECRRepository)
