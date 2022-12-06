from . import resources
from ._base import ResourceBase


class IAMServiceSpecificCredential(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        from .IAMUsers import IAMUser

        results = []
        try:
            iam_user = IAMUser(self.svc, self.region, self.filter_func)
            users, err = iam_user.list(has_cache=True)
            if err:
                return results, err

            results = results
            for user in users:
                reason, err = iam_user.filter(user)
                if err or reason:
                    continue

                user_name = user["id"]
                try:
                    creds = self.svc.list_service_specific_credentials(
                        UserName=user_name
                    )
                    if not creds:
                        return results, None
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
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_service_specific_credential(
                UserName=resource["user_name"],
                ServiceSpecificCredentialId=resource["id"],
            )
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
    resources.append(IAMServiceSpecificCredential)
