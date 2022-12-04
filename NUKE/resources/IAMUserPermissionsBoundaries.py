from . import resources
from ._base import ResourceBase
from .IAMUsers import IAMUser


class IAMUserPermissionsBoundary(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iam_user = IAMUser(sess=self.svc, default_filter_func=self.filter_func)
            users, err = iam_user.list(has_cache=True)
            if err:
                return results, err

            for user in users:
                reason, err = iam_user.filter(user)
                if err or reason:
                    continue

                if "PermissionsBoundary" not in user:
                    continue

                user_name = user["id"]
                results.append(
                    {
                        "id": user_name,
                        "name": (pb := user["PermissionsBoundary"])[
                            "PermissionsBoundaryArn"
                        ],
                        "arn": pb["PermissionsBoundaryArn"],
                        "type": pb["PermissionsBoundaryType"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_user_permissions_boundary(UserName=resource["id"])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            ), None
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
    resources.append(IAMUserPermissionsBoundary)
