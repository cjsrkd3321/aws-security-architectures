from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class IAMOpenIdConnectProvider(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            oidcs = self.svc.list_open_id_connect_providers()[
                "OpenIDConnectProviderList"
            ]
            for oidc in oidcs:
                oidc_arn = oidc["Arn"]
                try:
                    tags = self.svc.list_open_id_connect_provider_tags(
                        OpenIDConnectProviderArn=oidc_arn
                    )["Tags"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": oidc_arn,
                        "name": oidc_arn,
                        "tags": tags,
                        "arn": oidc_arn,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_open_id_connect_provider(
                OpenIDConnectProviderArn=resource["id"]
            )
            return True, None
        except self.exceptions.NoSuchEntityException:
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
    resources.append(IAMOpenIdConnectProvider)
