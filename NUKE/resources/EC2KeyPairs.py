from ._base import ResourceBase
from . import resources, Config

import boto3


class EC2KeyPair(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
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
                        "create_date": pair["CreateTime"],
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_key_pair(KeyName=resource["id"])["ResponseMetadata"][
                    "HTTPStatusCode"
                ]
                == 200
            ), None
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
