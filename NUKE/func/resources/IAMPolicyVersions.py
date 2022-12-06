from ._base import ResourceBase
from . import resources


class IAMPolicyVersion(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        from .IAMPolicies import IAMPolicy

        results = []
        try:
            iam_policy = IAMPolicy(self.svc, self.region, self.filter_func)
            policies, err = iam_policy.list(has_cache=True)
            if err:
                return results, err

            for policy in policies:
                reason, err = iam_policy.filter(policy)
                if err or reason:
                    continue

                policy_arn = policy["arn"]
                try:
                    versions = self.svc.list_policy_versions(PolicyArn=policy_arn)
                    if not versions:
                        return results, None
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
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_policy_version(
                PolicyArn=resource["policy_arn"], VersionId=resource["id"]
            )
            return True, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["is_default"]:
            return f"DEFAULT(IMPOSSIBLE: {resource['is_default']})", None
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
