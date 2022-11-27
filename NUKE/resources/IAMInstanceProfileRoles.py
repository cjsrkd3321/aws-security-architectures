from . import resources, Config
from ._base import ResourceBase
from .IAMRoles import IAMRole


import boto3


class IAMInstanceProfileRole(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iam_role = IAMRole(default_filter_func=self.filter_func)
            roles, err = iam_role.list()
            if err:
                return [], err
            filtered_roles, err = iam_role.filter(roles)
            if err:
                return [], err

            results = []
            for role in filtered_roles:
                role_name = role["id"]
                try:
                    instance_profiles = self.svc.list_instance_profiles_for_role(
                        RoleName=role_name
                    )
                    if not instance_profiles:
                        return [], None
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
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.remove_role_from_instance_profile(
                    RoleName=resource["role_name"], InstanceProfileName=resource["id"]
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
    resources.append(IAMInstanceProfileRole)
