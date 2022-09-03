import os
import time
import boto3
from botocore.config import Config

from libs.ec2 import get_available_instances, get_available_regions


EC2_DEFAULT_ROLE = os.getenv("EC2_DEFAULT_ROLE")
SSM_MANAGED_POLICY = os.getenv("SSM_MANAGED_POLICY")
INSTANCE_PROFILE_ARN = os.getenv("INSTANCE_PROFILE_ARN")
INSTANCE_PROFILE_NAME = os.getenv("INSTANCE_PROFILE_NAME")


iam = boto3.client("iam")


def lambda_handler(event, context):
    association_ids = []

    for region in get_available_regions():
        print(f"[{region}]")
        ec2 = boto3.client("ec2", config=Config(region_name=region))

        for instance in get_available_instances(ec2):
            instance_id = instance["InstanceId"]

            # 인스턴스 프로파일 없을 경우 붙여줌
            if not instance.get("IamInstanceProfile", False):
                result = ec2.associate_iam_instance_profile(
                    IamInstanceProfile={
                        "Arn": INSTANCE_PROFILE_ARN,
                        "Name": INSTANCE_PROFILE_NAME,
                    },
                    InstanceId=instance["InstanceId"],
                )["IamInstanceProfileAssociation"]

                if result["State"] == "associating":
                    association_ids.append(result["AssociationId"])
                    print(
                        f"[+] {instance['InstanceId']} 에 {INSTANCE_PROFILE_NAME} 인스턴스 프로파일 부여 완료."
                    )
            # 인스턴스 프로파일 있을 경우 SSM 정책 있는지 확인
            else:
                instance_profile_name = instance["IamInstanceProfile"]["Arn"].split(
                    "/"
                )[-1]
                roles = iam.get_instance_profile(
                    InstanceProfileName=instance_profile_name
                )["InstanceProfile"]["Roles"]
                role_name = [role["RoleName"] for role in roles][0]
                attached_policies = iam.list_attached_role_policies(RoleName=role_name)[
                    "AttachedPolicies"
                ]
                policy_arns = [
                    policy_arn["PolicyArn"] for policy_arn in attached_policies
                ]

                if SSM_MANAGED_POLICY not in policy_arns:
                    res = iam.attach_role_policy(
                        RoleName=role_name, PolicyArn=SSM_MANAGED_POLICY
                    )
                    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
                        print(f"[+] {role_name} 역할에 {SSM_MANAGED_POLICY} 정책 부여 완료.")
                else:
                    print(f"[{instance_id}] 은(는) 문제없음")

        # 인스턴스 프로파일 부여 완료되는 것 확인
        while True:
            associations = ec2.describe_iam_instance_profile_associations(
                AssociationIds=association_ids,
                Filters=[{"Name": "state", "Values": ["associating"]}],
            )["IamInstanceProfileAssociations"]
            if not associations:
                break

            time.sleep(0.5)

    if association_ids:
        print(f"\n[+] 모든 인스턴스에 프로파일이 부여되었습니다.")
    else:
        print(f"\n[+] 모든 인스턴스 프로파일에 권한이 부여되어 있습니다.")

    return
