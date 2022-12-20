import boto3

iam = boto3.client("iam")


def console_login(lock_type, args, deny_policy):
    user_name, role_name = args
    if user_name == "root" or role_name.startswith("AWSReservedSSO_"):
        raise Exception(f"[ConsoleLogin] {user_name} or {role_name} can't lock.")
    if lock_type == "ACTION":
        if role_name:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=deny_policy)
        else:
            iam.attach_user_policy(UserName=user_name, PolicyArn=deny_policy)
    else:
        if role_name:
            iam.detach_role_policy(RoleName=role_name, PolicyArn=deny_policy)
        else:
            iam.detach_user_policy(UserName=user_name, PolicyArn=deny_policy)
