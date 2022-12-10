from os import getenv
from concurrent import futures

from filters import have_no_nuke_project_tag, have_tags, is_create_date_less_than_now
from items import Item
from resources import resources
from resources.utils import get_regions, get_sessions
from resources.aws._GLOBAL import SERVICES

import time
import json


IS_RUN_DELETE = getenv("IS_RUN_DELETE", "FALSE")
MAX_WORKERS = int(getenv("MAX_WORKERS", 500))
MAX_ITER_COUNTS = int(getenv("MAX_ITER_COUNTS", 50))
MAX_SLEEP = int(getenv("MAX_SLEEP", 15))
REGIONS = get_regions()
REGIONS = ["us-east-1", "ap-northeast-2"]


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
    # STARTED_AT = time.time() # You must calculate time because of lambda maximum operating time.
    items = {"REMOVED": [], "FAILED": [], "FILTERED": []}
    global MAX_ITER_COUNTS, MAX_SLEEP, MAX_WORKERS, REGIONS, SERVICES
    sessions = get_sessions(SERVICES, REGIONS)

    for iter_cnt in range(MAX_ITER_COUNTS):
        scan_results = []
        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        threads = []
        for region in REGIONS:
            services = sessions[region].keys()
            if not services:
                continue

            threads += [
                pool.submit(lister, r, sessions[region][svc], have_no_nuke_project_tag)
                # pool.submit(lister, r, sessions[region][svc], is_create_date_less_than_now)
                # pool.submit(lister, r, sessions[region][svc], have_tags)
                # pool.submit(lister, r, sessions[region][svc])
                for r in resources
                for svc in services
                if r.__name__.lower().startswith(svc.replace("-", ""))
            ]
        for future in futures.as_completed(threads):
            scan_results += future.result()

        for item in scan_results:
            if item.filter():
                items["FILTERED"].append(item.current)
                continue

            if IS_RUN_DELETE == "FALSE":
                continue

            items["REMOVED" if item.remove() else "FAILED"].append(item.current)

        if (len(items["FAILED"]) == 0) or (iter_cnt == MAX_ITER_COUNTS - 1):
            print(json.dumps(items, indent=2).replace('"', ""))
            print(
                f"FILTERED: {len(items['FILTERED'])}, REMOVED: {len(items['REMOVED'])}, FAILED: {len(items['FAILED'])}"
            )
            break

        items["FAILED"].clear() or items["FILTERED"].clear()
        print(f"\nWaiting {MAX_SLEEP} seconds...\n")
        time.sleep(MAX_SLEEP)


if __name__ == "__main__":
    lambda_handler("event", "context")
