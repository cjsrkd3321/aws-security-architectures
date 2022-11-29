from concurrent import futures
from resources import resources
from filters import have_tags
from items import Item, items

import time
import boto3


MAX_WORKERS = 16
MAX_ITER_COUNTS = 3
MAX_SLEEP = 5


def get_regions(ec2):
    return [region.get("RegionName") for region in ec2.describe_regions()["Regions"]]


def lister(resource, region):
    global items

    r = resource(region, default_filter_func=have_tags)
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


if __name__ == "__main__":
    ec2 = boto3.client("ec2")
    regions = get_regions(ec2)

    for _ in range(MAX_ITER_COUNTS):
        threads = []

        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in regions:
            for resource in resources:
                threads.append(pool.submit(lister, resource, region))
        futures.wait(threads)

        for item in items:
            item.filter()

            if item.is_skip():
                print(item.current)
                continue
            else:
                print(item.current)

            # item.remove()
            # print(item.current)

        items.clear()

        print(f"\nWaiting {MAX_SLEEP} seconds...\n")
        time.sleep(MAX_SLEEP)
