from os import getenv
from concurrent import futures

from filters import have_no_nuke_project_tag, have_tags, is_create_date_less_than_now
from items import Item
from resources import resources
from resources.utils import get_regions, get_sessions
from resources.aws._GLOBAL import SERVICES

from time import sleep, time
from json import dumps


IS_RUN_DELETE = getenv("IS_RUN_DELETE", "TRUE")
MAX_WORKERS = int(getenv("MAX_WORKERS", 500))
MAX_ITER_COUNTS = int(getenv("MAX_ITER_COUNTS", 50))
MAX_SLEEP = int(getenv("MAX_SLEEP", 15))
MAX_RUNNING_TIME = getenv("MAX_RUNNING_TIME", 850)
TOPIC_ARN = getenv("TOPIC_ARN", "")
REGIONS = get_regions()


def lister(resource, sess, filter_func=None):
    name = resource.__name__
    region = sess._client_config.region_name
    lister_results = []

    try:
        r = resource(sess, filter_func)
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
        lister_results.append(item)
    return lister_results


def lambda_handler(event, context):
    if not TOPIC_ARN:
        print("You must set the TOPIC_ARN environment variable.")
        return

    global MAX_ITER_COUNTS, MAX_SLEEP, MAX_WORKERS, REGIONS, SERVICES
    STARTED_AT = time()

    message = ""
    items = {"REMOVED": [], "FAILED": [], "FILTERED": []}
    sessions = get_sessions(SERVICES, REGIONS)

    for iter_cnt in range(MAX_ITER_COUNTS):
        list_start_time = time()

        scan_results = []
        threads = []
        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in REGIONS:
            services = sessions[region].keys()
            if not services:
                continue

            threads += [
                # pool.submit(lister, r, sessions[region][svc], have_no_nuke_project_tag) # FOR TEST
                # pool.submit(lister, r, sessions[region][svc], is_create_date_less_than_now)
                pool.submit(lister, r, sessions[region][svc], have_tags)  # NO TAGS
                # pool.submit(lister, r, sessions[region][svc]) # ALL RESOURCES
                for r in resources
                for svc in services
                if r.__name__.lower().startswith(svc.replace("-", ""))
            ]
        for future in futures.as_completed(threads):
            scan_results += future.result()

        print(f"LIST ELAPSED TIME: {time() - list_start_time:.3f}s")

        filter_remove_start_time = time()

        for item in scan_results:
            if item.filter():
                items["FILTERED"].append(item.current)
                continue

            if IS_RUN_DELETE == "FALSE":
                continue

            items["REMOVED" if item.remove() else "FAILED"].append(item.current)
            print(item.current)

        elapsed_time = int(time() - STARTED_AT)
        if (
            (len(items["FAILED"]) == 0)
            or (iter_cnt == MAX_ITER_COUNTS - 1)
            or elapsed_time > MAX_RUNNING_TIME
        ):
            message += dumps(items, indent=2).replace('"', "")
            message += f"\nFILTERED: {len(items['FILTERED'])}, REMOVED: {len(items['REMOVED'])}, FAILED: {len(items['FAILED'])}"
            break

        print(f"F&R ELAPSED TIME: {time() - filter_remove_start_time:.3f}s")

        items["FAILED"].clear() or items["FILTERED"].clear()
        print(f"\nWaiting {MAX_SLEEP} seconds...\n")
        sleep(MAX_SLEEP)

    from datetime import date
    import boto3

    sns = boto3.client("sns")
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=message,
        Subject=f"{date.today()} - AWS NUKE RESULTS",
    )


if __name__ == "__main__":
    lambda_handler("event", "context")
