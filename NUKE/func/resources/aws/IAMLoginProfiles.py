from resources import resources
from resources.base import ResourceBase


class IAMLoginProfile(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        from .IAMUsers import IAMUser

        results = []
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
                    p = self.svc.get_login_profile(UserName=user_name)["LoginProfile"]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": user_name,
                        "name": user_name,
                        "create_date": p["CreateDate"],
                        "password_reset_required": p["PasswordResetRequired"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_login_profile(UserName=resource["id"])
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
    resources.append(IAMLoginProfile)
