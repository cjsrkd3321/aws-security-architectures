from ._base import ResourceBase
from . import resources, Config

import boto3


class IAMInstanceProfile(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iterator = self.svc.get_paginator("list_instance_profiles").paginate()

            results = []
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
            return [], e

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

    def filter(self, resources, *filters):
        if not resources:
            return [], None
        filtered_resources = [r for r in resources if not r["have_roles"]]
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
    resources.append(IAMInstanceProfile)
