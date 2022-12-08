from resources import resources
from resources.base import ResourceBase


class IAMMfaDevice(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        from .IAMUsers import IAMUser

        results = []
        try:
            iam_user = IAMUser(self.svc, self.filter_func)
            users, err = iam_user.list(has_cache=True)
            if err:
                return results, err

            for user in users:
                reason, err = iam_user.filter(user)
                if err or reason:
                    continue

                user_name = user["id"]
                try:
                    devices = self.svc.list_mfa_devices(UserName=user_name)
                    if not devices:
                        return results, None
                    results += [
                        {
                            "id": device["SerialNumber"],
                            "name": device["SerialNumber"],
                            "user_name": user_name,
                        }
                        for device in devices["MFADevices"]
                    ]
                except self.exceptions.NoSuchEntityException:
                    continue
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.deactivate_mfa_device(
                UserName=resource["user_name"], SerialNumber=resource["id"]
            )
            self.svc.delete_virtual_mfa_device(SerialNumber=resource["id"])
            return True, None
        except self.exceptions.NoSuchEntityException:
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if resource["id"].endswith("/root-account-mfa-device"):
            return f"DEFAULT(IMPOSSIBLE: {resource['id']})", None
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
    resources.append(IAMMfaDevice)
