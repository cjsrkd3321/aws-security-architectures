from resources import resources
from resources.base import ResourceBase


class SECRETSMANAGERSecret(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None):
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("list_secrets").paginate()
            secrets = [s for secrets in iterator for s in secrets["SecretList"]]
            for secret in secrets:
                results.append(
                    {
                        "id": secret["ARN"],
                        "name": secret["Name"],
                        "arn": secret["ARN"],
                        "tags": secret.get("Tags", []),
                        "create_date": secret["CreatedDate"],
                        "description": secret.get("Description"),
                        "is_rotated": secret.get("RotationEnabled", False),
                        "delete_date": secret.get("DeletedDate"),
                        "last_rotated_date": secret.get("LastRotatedDate"),
                        "last_changed_date": secret.get("LastChangedDate"),
                        "last_used_date": secret.get("LastAccessedDate"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_secret(
                SecretId=resource["id"], ForceDeleteWithoutRecovery=True
            )
            return True, None
        except self.exceptions.ResourceNotFoundException:
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
    resources.append(SECRETSMANAGERSecret)
