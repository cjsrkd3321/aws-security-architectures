from os import getenv
from concurrent import futures

from filters import have_no_nuke_project_tag, have_tags, is_create_date_less_than_now
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
    "sns",
    "grafana",
    "eks",
    "emr",
]
REGIONS = get_regions()
REGIONS = ["ap-northeast-2"]


def lister(resource, sess):
    name = resource.__name__
    region = sess._client_config.region_name

    try:
        r = resource(sess, have_no_nuke_project_tag)
        # r = resource(sess, is_create_date_less_than_now)
        # r = resource(sess, have_tags)
    except Exception as e:
        print("[ERR_INIT]", name, e)
        return

    resource_results, err = r.list()
    if err:
        print("[ERR_LIST]", name, err)
        return

    for resource_result in resource_results:
        item = Item(
            resource=resource_result,
            region="us-east-1" if region == "aws-global" else region,
            name=name,
            filterer=r.filter,
            remover=r.remove,
        )
        items.append(item)


def lambda_handler(event, context):
    global MAX_ITER_COUNTS, MAX_SLEEP, MAX_WORKERS, REGIONS, SERVICES

    sessions = get_sessions(SERVICES, REGIONS)

    for _ in range(MAX_ITER_COUNTS):
        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in REGIONS:
            services = sessions[region].keys()
            if not services:
                continue

            threads = [
                pool.submit(lister, r, sessions[region][svc])
                for r in resources
                for svc in services
                if r.__name__.lower().startswith(svc)
            ]
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
                    "is_create_date_less_than_now",
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
    lambda_handler("event", "context")
