from ._base import ResourceBase
from . import resources


class EC2KeyPair(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["ec2"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            pairs = self.svc.describe_key_pairs()["KeyPairs"]
            for pair in pairs:
                results.append(
                    {
                        "id": pair["KeyName"],
                        "unique_id": pair["KeyPairId"],
                        "tags": pair.get("Tags", []),
                        "name": pair["KeyName"],
                        "create_date": pair.get("CreateTime"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.delete_key_pair(KeyName=resource["id"])
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
    resources.append(EC2KeyPair)
