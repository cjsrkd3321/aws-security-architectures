from ._base import ResourceBase
from . import resources, Config
from .IAMPolicies import IAMPolicy

import boto3


class IAMPolicyVersion(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("iam", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        try:
            iam_policy = IAMPolicy(default_filter_func=self.filter_func)
            policies, err = iam_policy.list()
            if err:
                return [], err

            results = []
            for policy in policies:
                policy, err = iam_policy.filter(policy)
                if err or policy:
                    continue

                policy_arn = policy["arn"]
                try:
                    versions = self.svc.list_policy_versions(PolicyArn=policy_arn)
                    if not versions:
                        return [], None
                    results += [
                        {
                            "id": version["VersionId"],
                            "name": version["VersionId"],
                            "is_default": version["IsDefaultVersion"],
                            "create_date": version["CreateDate"],
                            "policy_arn": policy_arn,
                        }
                        for version in versions["Versions"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return [], e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_policy_version(
                    PolicyArn=resource["policy_arn"], VersionId=resource["id"]
                )["ResponseMetadata"]["HTTPStatusCode"]
                == 200
            ), None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["is_default"]:
            return "default rule", None
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
    resources.append(IAMPolicyVersion)
