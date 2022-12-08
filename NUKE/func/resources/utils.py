from functools import wraps
from botocore.config import Config
from boto3.session import Session

import time
import boto3


SESSIONS: dict = {}


def get_name_from_tags(tags):
    if not tags:
        return None
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None


def has_value_from_tags(tags, key, value):
    if not tags:
        return False
    for tag in tags:
        if tag.get("Key") == key:
            return tag.get("Value") == value
    return False


def delete_tag_prefix(tags):
    new_tags = []
    if not tags:
        return new_tags
    for tag in tags:
        key, value = tag.items()
        new_tags.append({"Key": key[1], "Value": value[1]})
    return new_tags


def convert_dict_to_tags(tags):
    new_tags = []
    if not tags:
        return new_tags
    for key, value in tags.items():
        new_tags.append({"Key": key, "Value": value})
    return new_tags


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper


def get_regions():
    ec2 = boto3.client("ec2")
    return [region.get("RegionName") for region in ec2.describe_regions()["Regions"]]


def get_sessions(services=[], regions=[]):
    global SESSIONS
    GLOBAL_REGION = "us-east-1"

    sess = Session()
    for service in services:
        if service in ["iam"]:
            SESSIONS[GLOBAL_REGION] = {
                service: boto3.client(
                    service_name=service,
                    config=Config(region_name=GLOBAL_REGION, max_pool_connections=1000),
                )
            }
            continue

        available_regions = sess.get_available_regions(service_name=service)
        for available_region in available_regions:
            if not SESSIONS.get(available_region):
                SESSIONS[available_region] = {}
            if available_region not in regions:
                continue
            SESSIONS[available_region][service] = boto3.client(
                service_name=service,
                config=Config(region_name=available_region, max_pool_connections=1000),
            )

    return SESSIONS
