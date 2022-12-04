from . import resources
from ._base import ResourceBase
from .IAMRoles import IAMRole


class IAMRolePolicy(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iam_role = IAMRole(self.svc, self.region, self.filter_func)
            roles, err = iam_role.list(has_cache=True)
            if err:
                return results, err

            for role in roles:
                reason, err = iam_role.filter(role)
                if err or reason:
                    continue

                role_name = role["id"]
                try:
                    policies = self.svc.list_role_policies(RoleName=role_name)
                    if not policies:
                        return results, None
                    results += [
                        {
                            "id": policy,
                            "name": policy,
                            "role_name": role_name,
                        }
                        for policy in policies["PolicyNames"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_role_policy(
                    RoleName=resource["role_name"], PolicyName=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
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
    resources.append(IAMRolePolicy)
