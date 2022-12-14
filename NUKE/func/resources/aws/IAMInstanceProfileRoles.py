from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults


class IAMInstanceProfileRole(ResourceBase):
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
                    instance_profiles = self.svc.list_instance_profiles_for_role(
                        RoleName=role_name
                    )
                    if not instance_profiles:
                        return results, None
                    results += [
                        {
                            "id": instance_profile["InstanceProfileName"],
                            "name": instance_profile["InstanceProfileName"],
                            "role_name": role_name,
                            "arn": instance_profile["Arn"],
                            "create_date": instance_profile["CreateDate"],
                            "path": instance_profile["Path"],
                            "unique_id": instance_profile["InstanceProfileId"],
                        }
                        for instance_profile in instance_profiles["InstanceProfiles"]
                        if "Roles" in instance_profile
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.remove_role_from_instance_profile(
                RoleName=resource["role_name"], InstanceProfileName=resource["id"]
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
    resources.append(IAMInstanceProfileRole)
