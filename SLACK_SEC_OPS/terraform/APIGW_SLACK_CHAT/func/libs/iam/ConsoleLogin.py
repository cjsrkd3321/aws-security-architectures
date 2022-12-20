from botocore.config import Config
from libs import actors

import boto3


class ConsoleLogin:
    def __init__(self, region, args, deny_policy):
        self.client = boto3.client("iam", config=Config(region_name=region))
        self.user, self.role = args
        self.policy = deny_policy

    def do(self, func, act_type):
        if self.role:
            self.client.attach_role_policy(RoleName=self.role, PolicyArn=self.policy)
        else:
            self.client.attach_user_policy(UserName=self.user, PolicyArn=self.policy)
        func(act_type)

    def undo(self, func, act_type):
        if self.role:
            self.client.detach_role_policy(RoleName=self.role, PolicyArn=self.policy)
        else:
            self.client.detach_user_policy(UserName=self.user, PolicyArn=self.policy)
        func(act_type)


if __name__ != "__main__":
    actors[ConsoleLogin.__name__] = ConsoleLogin
