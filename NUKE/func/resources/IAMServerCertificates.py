from ._base import ResourceBase
from . import resources


class IAMServerCertificate(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_server_certificates").paginate()
            certs = [
                cert
                for certs in iterator
                for cert in certs["ServerCertificateMetadataList"]
            ]
            for cert in certs:
                cert_name = cert["ServerCertificateName"]

                try:
                    c = self.svc.get_server_certificate(
                        ServerCertificateName=cert_name
                    )["ServerCertificate"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": cert_name,
                        "name": cert_name,
                        "path": (meta := c["ServerCertificateMetadata"])["Path"],
                        "tags": c.get("Tags", []),
                        "arn": meta["Arn"],
                        "unique_id": meta["ServerCertificateId"],
                        "create_date": meta["UploadDate"],
                        "expire_date": meta["Expiration"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_server_certificate(ServerCertificateName=resource["id"])
            return True, None
        except self.exceptions.NoSuchEntityException:
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
    resources.append(IAMServerCertificate)
