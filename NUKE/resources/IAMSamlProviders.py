from ._base import ResourceBase
from . import resources


class IAMSamlProvider(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            samls = self.svc.list_saml_providers()["SAMLProviderList"]
            for saml in samls:
                saml_arn = saml["Arn"]
                try:
                    tags = self.svc.list_saml_provider_tags(SAMLProviderArn=saml_arn)[
                        "Tags"
                    ]
                except self.exceptions.NoSuchEntityException:
                    tags = []

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

    def remove(self, resource):
        try:
            self.svc.delete_saml_provider(SAMLProviderArn=resource["id"])
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
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
