from . import resources, Config
from ._base import ResourceBase
from .IAMUsers import IAMUser


import boto3


class IAMServiceSpecificCredential(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iam_user = IAMUser(default_filter_func=self.filter_func)
            users, err = iam_user.list()
            if err:
                return [], err
            filtered_users, err = iam_user.filter(users)
            if err:
                return [], err

            results = []
            for user in filtered_users:
                user_name = user["id"]
                try:
                    creds = self.svc.list_service_specific_credentials(
                        UserName=user_name
                    )
                    if not creds:
                        return [], None
                    results += [
                        {
                            "id": cred["ServiceSpecificCredentialId"],
                            "name": cred["ServiceName"],
                            "user_name": user_name,
                            "create_date": cred["CreateDate"],
                            "state": cred["Status"],
                        }
                        for cred in creds["ServiceSpecificCredentials"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_service_specific_credential(
                    UserName=resource["user_name"],
                    ServiceSpecificCredentialId=resource["id"],
                )["ResponseMetadata"]["HTTPStatusCode"]
            ) == 200, None
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
    resources.append(IAMServiceSpecificCredential)
