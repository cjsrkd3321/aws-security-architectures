from . import resources, Config
from ._base import ResourceBase
from ._utils import filter_func
from .IAMUsers import IAMUser


import boto3


class IAMSigningCertificate(ResourceBase):
    def __init__(self, region="ap-northeast-2") -> None:
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions

    def list(self):
        try:
            iam_user = IAMUser()
            users, err = iam_user.list()
            if err:
                return [], err
            filtered_users, err = iam_user.filter(users, filter_func)
            if err:
                return [], err

            results = []
            for user in filtered_users:
                user_name = user["id"]
                try:
                    certs = self.svc.list_signing_certificates(UserName=user_name)
                    if not certs:
                        return [], None
                    results += [
                        {
                            "id": cert["CertificateId"],
                            "name": cert["CertificateId"],
                            "user_name": user_name,
                            "create_date": cert["UploadDate"],
                            "tags": [],
                        }
                        for cert in certs["Certificates"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_signing_certificate(
                    UserName=resource["user_name"], CertificateId=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
            ) == 200, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resources, filter_func=None):
        if not resources:
            return [], None
        filtered_resources = resources
        if filter_func:
            try:
                filtered_resources = filter_func(filtered_resources)
            except Exception as e:
                return [], e
        return filtered_resources, None

    def properties(self):
        pass


if __name__ == "__main__":
    role = IAMSigningCertificate()
    print(role.filter(role.list()))
else:
    resources.append(IAMSigningCertificate)
    if IAMUser in resources:
        resources.remove(IAMUser)
