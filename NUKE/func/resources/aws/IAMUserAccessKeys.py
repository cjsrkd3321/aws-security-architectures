from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class IAMUserAccessKey(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        from .IAMUsers import IAMUser

        results: list = []
        try:
            iam_user = IAMUser(self.svc, self.filter_func)
            users, err = iam_user.list(has_cache=True)
            if err:
                return results, err

            for user in users:
                reason, err = iam_user.filter(user)
                if err or reason:
                    continue

                user_name = user["id"]
                try:
                    access_keys = self.svc.list_access_keys(UserName=user_name)
                    if not access_keys:
                        return results, None

                    for access_key in access_keys["AccessKeyMetadata"]:
                        try:
                            k = self.svc.get_access_key_last_used(
                                AccessKeyId=access_key["AccessKeyId"]
                            )["AccessKeyLastUsed"]
                        except self.exceptions.NoSuchEntityException:
                            k = {}

                        results.append(
                            {
                                "id": access_key["AccessKeyId"],
                                "name": access_key["AccessKeyId"],
                                "user_name": user_name,
                                "state": access_key["Status"],
                                "create_date": access_key["CreateDate"],
                                "last_used_date": k.get("LastUsedDate"),
                            }
                        )
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.delete_access_key(
                UserName=resource["user_name"], AccessKeyId=resource["id"]
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
    resources.append(IAMUserAccessKey)
