from . import resources
from ._base import ResourceBase
from .IAMUsers import IAMUser


class IAMUserPolicyAttachment(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

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

                user_name = user["id"]
                try:
                    attached_policies = self.svc.list_attached_user_policies(
                        UserName=user_name
                    )
                    if not attached_policies:
                        return results, None
                    results += [
                        {
                            "id": policy["PolicyArn"],
                            "name": policy["PolicyName"],
                            "user_name": user_name,
                            "arn": policy["PolicyArn"],
                        }
                        for policy in attached_policies["AttachedPolicies"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.detach_user_policy(
                    UserName=resource["user_name"], PolicyArn=resource["id"]
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
    resources.append(IAMUserPolicyAttachment)
