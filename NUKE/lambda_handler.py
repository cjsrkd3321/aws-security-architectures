from concurrent import futures
from resources import resources
from filters import have_tags
from items import Item, items

import time
import boto3


MAX_WORKERS = 16


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
    try:
        ec2 = boto3.client("ec2")
        regions = get_regions(ec2)

        threads = []

        pool = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        for region in regions:
            for resource in resources:
                threads.append(pool.submit(lister, resource, region))
        futures.wait(threads)

        for _ in range(60):
            for sr in items:
                if sr.is_skip():
                    continue

                sr.filter()
                sr.remove()
                print(sr.current)
            time.sleep(1)
    except Exception as e:
        print(e)
        exit(1)
