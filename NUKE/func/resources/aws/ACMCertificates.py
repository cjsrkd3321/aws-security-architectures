from resources import resources
from resources.base import ResourceBase


class ACMCertificate(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_certificates").paginate()
            certs = [c for certs in iterator for c in certs["CertificateSummaryList"]]
            for cert in certs:
                arn = cert["CertificateArn"]
                try:
                    tags = self.svc.list_tags_for_certificate(CertificateArn=arn)
                except self.exceptions.ResourceNotFoundException:
                    continue
                results.append(
                    {
                        "id": arn,
                        "name": cert["DomainName"],
                        "tags": tags["Tags"],
                        "arn": arn,
                        "state": cert["Status"],
                        "create_date": cert["CreatedAt"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_certificate(CertificateArn=resource["id"])
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
    resources.append(ACMCertificate)
