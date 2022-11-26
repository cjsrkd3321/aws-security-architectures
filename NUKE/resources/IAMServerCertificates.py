from ._base import ResourceBase
from . import resources, Config

import boto3


class IAMServerCertificate(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("list_server_certificates").paginate()

            results = []
            certs = [
                cert
                for certs in iterator
                for cert in certs["ServerCertificateMetadataList"]
            ]
            for cert in certs:
                cert_name = cert["ServerCertificateName"]

                try:
                    c = self.svc.get_server_certificate(RoleName=cert_name)[
                        "ServerCertificate"
                    ]
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
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_server_certificate(
                    ServerCertificateName=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            ), None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resources, *filters):
        if not resources:
            return [], None
        filtered_resources = resources
        if self.filter_func:
            try:
                filtered_resources = self.filter_func(filtered_resources)
            except Exception as e:
                return [], e
        for filter in filters:
            filtered_resources = filter(filtered_resources)
        return filtered_resources, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(IAMServerCertificate)
