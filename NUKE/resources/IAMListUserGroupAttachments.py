from . import resources
from ._base import ResourceBase


class IAMListUserGroupAttachment(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["iam"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        from .IAMUsers import IAMUser

        results = []
        try:
            iam_user = IAMUser(self.svc, self.region, self.filter_func)
            users, err = iam_user.list(has_cache=True)
            if err:
                return results, err

            for user in users:
                reason, err = iam_user.filter(user)
                if err or reason:
                    continue

                user_name = user["id"]
                try:
                    groups = self.svc.list_groups_for_user(UserName=user_name)
                    if not groups:
                        return results, None
                    results += [
                        {
                            "id": group["GroupName"],
                            "name": group["GroupName"],
                            "user_name": user_name,
                            "create_date": group["CreateDate"],
                            "arn": group["Arn"],
                            "path": group["Path"],
                            "unique_id": group["GroupId"],
                        }
                        for group in groups["Groups"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.remove_user_from_group(
                UserName=resource["user_name"], GroupName=resource["id"]
            )
            return True, None
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
    resources.append(IAMListUserGroupAttachment)
