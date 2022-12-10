from resources import resources
from resources.base import ResourceBase


class ACMPCACertificateAuthority(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []

        # Check if self.svc create from acm not acm-pca
        if "list_certificate_authorities" not in dir(self.svc):
            return results, None

        try:
            iterator = self.svc.get_paginator("list_certificate_authorities").paginate()
            cas = [ca for cas in iterator for ca in cas["CertificateAuthorities"]]
            for ca in cas:
                arn = ca["Arn"]
                try:
                    tags = self.svc.list_tags(CertificateAuthorityArn=arn)["Tags"]
                except (
                    self.exceptions.ResourceNotFoundException,
                    self.exceptions.InvalidStateException,
                ):
                    continue
                results.append(
                    {
                        "id": arn,
                        "name": arn,
                        "tags": tags,
                        "arn": arn,
                        "state": ca["Status"],
                        "create_date": ca["CreatedAt"],
                        "last_modified_date": ca.get("LastStateChangeAt"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_certificate_authority(
                CertificateAuthorityArn=resource["id"], PermanentDeletionTimeInDays=7
            )
            return True, None
        except self.exceptions.ResourceNotFoundException:
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
    resources.append(ACMPCACertificateAuthority)
