import boto3


def get_available_regions():
    ec2 = boto3.client("ec2")
    return [region["RegionName"] for region in ec2.describe_regions()["Regions"]]


def get_available_instances(ec2_client):
    instances = []

    reservations = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
    )["Reservations"]
    if not reservations:
        return instances

    for reservation in reservations:
        instances = [instance for instance in reservation["Instances"]]

    return instances
