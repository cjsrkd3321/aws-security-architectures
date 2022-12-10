from functools import wraps
from datetime import datetime
from botocore.config import Config
from boto3.session import Session

import time
import boto3


SESSIONS: dict = {}
MAX_POOL_CONNECTIONS = 1000


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
                    config=Config(
                        region_name=GLOBAL_REGION,
                        max_pool_connections=MAX_POOL_CONNECTIONS,
                    ),
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
                config=Config(
                    region_name=available_region,
                    max_pool_connections=MAX_POOL_CONNECTIONS,
                ),
            )
    return SESSIONS


def convert_time_to_datetime(date, utc):
    if type(date) == int:
        date = datetime.fromtimestamp(date / 1_000)
    elif type(date) == str:
        try:
            date = datetime.fromtimestamp(int(date))
        except ValueError:
            if date.endswith("Z"):
                date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    if not cd.tzinfo:
        cd = utc.localize(cd)
    cd = cd.replace(tzinfo=utc)
    return date
