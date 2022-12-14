from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class IAMSamlProvider(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        results: list = []
        try:
            samls = self.svc.list_saml_providers()["SAMLProviderList"]
            for saml in samls:
                saml_arn = saml["Arn"]
                try:
                    tags = self.svc.list_saml_provider_tags(SAMLProviderArn=saml_arn)[
                        "Tags"
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": saml_arn,
                        "name": saml_arn,
                        "arn": saml_arn,
                        "tags": tags,
                        "valid_date": saml["ValidUntil"],
                        "create_date": saml["CreateDate"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_saml_provider(SAMLProviderArn=resource["id"])
            return True, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
        name = resource["arn"].split("/")[-1]
        if name.startswith("AWSSSO_") and name.endswith("_DO_NOT_DELETE"):
            return f"DEFAULT(IMPOSSIBLE: {name})", None
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
    resources.append(IAMSamlProvider)
