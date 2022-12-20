from botocore.config import Config
from libs import actors

import boto3


class CreateAccessKey:
    def __init__(self, region, args, _):
        self.client = boto3.client("iam", config=Config(region_name=region))
        self.user, self.key_id = args

    def do(self, func, act_type):
        self.client.delete_access_key(UserName=self.user, AccessKeyId=self.key_id)
        func(act_type)

    def undo(self, _, __):
        pass


if __name__ != "__main__":
    actors[CreateAccessKey.__name__] = CreateAccessKey
