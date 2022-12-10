from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class IAMRolePolicyAttachment(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        from .IAMRoles import IAMRole

        results: list = []
        try:
            iam_role = IAMRole(self.svc, self.filter_func)
            roles, err = iam_role.list(has_cache=True)
            if err:
                return results, err

            for role in roles:
                reason, err = iam_role.filter(role)
                if err or reason:
                    continue

                role_name = role["id"]
                try:
                    attached_policies = self.svc.list_attached_role_policies(
                        RoleName=role_name
                    )
                    if not attached_policies:
                        return results, None
                    results += [
                        {
                            "id": policy["PolicyArn"],
                            "name": policy["PolicyName"],
                            "role_name": role_name,
                            "arn": policy["PolicyArn"],
                        }
                        for policy in attached_policies["AttachedPolicies"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.detach_role_policy(
                RoleName=resource["role_name"], PolicyArn=resource["id"]
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
    resources.append(IAMRolePolicyAttachment)
