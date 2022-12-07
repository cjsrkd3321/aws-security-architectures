from os import getenv
from concurrent import futures

from filters import have_no_nuke_project_tag, have_tags
from items import Item, items
from _types import Services
from resources import resources
from resources.utils import get_regions, get_sessions

import time


IS_RUN_DELETE = getenv("IS_RUN_DELETE", "FALSE")
MAX_WORKERS = int(getenv("MAX_WORKERS", 50))
MAX_ITER_COUNTS = int(getenv("MAX_ITER_COUNTS", 60))
MAX_SLEEP = int(getenv("MAX_SLEEP", 10))
SERVICES: Services = [
    "ec2",
    "iam",
    "s3",
    "kms",
    "lambda",
    "kafka",
    "secretsmanager",
    "ssm",
    "logs",
    "sqs",
    "dynamodb",
    "rds",
]
REGIONS = get_regions()
REGIONS = ["ap-northeast-2", "us-east-1"]


def lister(resource, sess, region):
    try:
        r = resource(sess, region, have_no_nuke_project_tag)
        # r = resource(sess, region, have_tags)
        name = r.__class__.__name__
    except Exception as e:
        print("[ERR_INIT]", region, name, e)
        return

    if name.startswith("IAM") and region != "us-east-1":
        return

    resource_results, err = r.list()
    if err:
        print("[ERR_LIST]", region, name, err)
        return

    for resource_result in resource_results:
        item = Item(
            resource=resource_result,
            region=region,
            name=name,
            filterer=r.filter,
            remover=r.remove,
        )
        items.append(item)


def lambda_handler(event, context):
    global MAX_ITER_COUNTS, MAX_SLEEP, MAX_WORKERS, REGIONS, SERVICES

    for _ in range(MAX_ITER_COUNTS):
        threads = []
        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in REGIONS:
            for resource in resources:
                sessions = get_sessions(SERVICES, REGIONS)
                job = pool.submit(lister, resource, sessions, region)
                threads.append(job)
        futures.wait(threads)

        if not items:
            break

        for item in items:
            item.filter()
            if item.is_skip():
                # Temporary if statement
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
            break

        items.clear()

        print(f"\nWaiting {MAX_SLEEP} seconds...\n")
        time.sleep(MAX_SLEEP)


if __name__ == "__main__":
    for _ in range(MAX_ITER_COUNTS):
        threads = []
        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in REGIONS:
            for resource in resources:
                sessions = get_sessions(SERVICES, REGIONS)
                job = pool.submit(lister, resource, sessions, region)
                threads.append(job)
        futures.wait(threads)

        if not items:
            break

        for item in items:
            item.filter()
            if item.is_skip():
                # Temporary if statement
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
            break

        items.clear()

        print(f"\nWaiting {MAX_SLEEP} seconds...\n")
        time.sleep(MAX_SLEEP)
