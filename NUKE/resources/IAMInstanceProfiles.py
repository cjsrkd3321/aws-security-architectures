from ._base import ResourceBase
from . import resources


class IAMInstanceProfile(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_instance_profiles").paginate()
            profiles = [
                profile
                for profiles in iterator
                for profile in profiles["InstanceProfiles"]
            ]
            for profile in profiles:
                profile_name = profile["InstanceProfileName"]

                try:
                    p = self.svc.get_instance_profile(InstanceProfileName=profile_name)[
                        "InstanceProfile"
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue

                results.append(
                    {
                        "id": profile_name,
                        "name": profile_name,
                        "path": p["Path"],
                        "tags": p.get("Tags", []),
                        "arn": p["Arn"],
                        "unique_id": p["InstanceProfileId"],
                        "create_date": p["CreateDate"],
                        "have_roles": True if "Roles" in p else False,
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_instance_profile(InstanceProfileName=resource["id"])[
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
    resources.append(IAMInstanceProfile)
