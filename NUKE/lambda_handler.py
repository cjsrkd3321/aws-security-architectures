from concurrent import futures
from time import sleep
from botocore.config import Config
from resources import resources
from filters import have_no_nuke_project_tag, have_tags
from items import Item, items
from _types import Services

import boto3


MAX_WORKERS = 25
MAX_ITER_COUNTS = 40
MAX_SLEEP = 15


def get_regions():
    ec2 = boto3.client("ec2")
    return [region.get("RegionName") for region in ec2.describe_regions()["Regions"]]


def lister(resource, sess, region):
    global items

    try:
        r = resource(sess, region, have_no_nuke_project_tag)
        # r = resource(sess, region, have_tags)
    except Exception as e:
        print("[ERR_INIT]", resource, region, e)

    name = r.__class__.__name__

    if name.startswith("IAM") and region != "us-east-1":
        return

    results, err = r.list()
    if err:
        print("[ERR_LIST]", name, err)

    for result in results:
        item = Item(
            resource=result,
            region=region,
            name=name,
            filterer=r.filter,
            remover=r.remove,
        )
        items.append(item)


def get_sessions(services=[], regions=[]):
    sessions = {}
    for region in regions:
        sessions[region] = {}
        for service in services:
            sessions[region][service] = boto3.client(
                service_name=service, config=Config(region_name=region)
            )
    return sessions


if __name__ == "__main__":
    regions = get_regions()
    # regions = ["ap-southeast-1"]  # Singapore
    # regions = ["us-east-1"]  # Virginia
    # regions = ["ap-northeast-2"]  # Seoul
    regions = ["ap-southeast-1", "us-east-1"]
    services: Services = [
        "ec2",
        "iam",
        "s3",
        "kms",
        "lambda",
        "kafka",
        "secretsmanager",
    ]

    sessions = get_sessions(services, regions)

    for _ in range(MAX_ITER_COUNTS):
        threads = []

        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in regions:
            for resource in resources:
                threads.append(pool.submit(lister, resource, sessions, region))
        futures.wait(threads)

        if not items:
            break

        for item in items:
            item.filter()

            if item.is_skip():
                if item.item["reason"] in [
                    "have_no_nuke_project_tag",
                    "have_tags",
                ] or item.item["reason"].startswith("DEFAULT(IMPOSSIBLE"):
                    continue
                print(item.current)
                continue
            else:
                print(item.current)
                pass

            # item.remove()
            # print(item.current)

        failed_count = 0
        for item in items:
            if item.is_failed():
                failed_count += 1
        if failed_count == 0:
            exit(1)

        items.clear()

        print(f"\nWaiting {MAX_SLEEP} seconds...\n")
        sleep(MAX_SLEEP)
