from pprint import pprint
from typing import Optional, List, Callable, Dict
from concurrent import futures

import time
import boto3
import resources


results: Dict = {}


# identifies untagged resources
def default_filter(resources):
    word = "tags"
    return [r for r in resources if word not in r or not r.get(word)]


def last_used_date_filter(resources):
    word = "last_used_date"
    return [r for r in resources if word in r and r.get(word) is None]


def get_regions(ec2) -> List[Optional[str]]:
    return [region.get("RegionName") for region in ec2.describe_regions()["Regions"]]


def work(resources: List[Callable], region):
    try:
        global results
        results[region] = {}
        for resource in resources:
            start_time = time.time()
            r = resource(region=region, default_filter_func=default_filter)

            class_name = r.__class__.__name__
            if class_name.startswith("IAM") and region != "us-east-1":
                continue

            results[region][class_name] = []

            rs, err = r.list()
            # print(class_name, rs, err)
            if err:
                print("[ERR_LIST]", class_name, err)
                continue

            filtered_resources, err = r.filter(rs)
            # print(class_name, filtered_resources, err)
            if err:
                print("[ERR_FILTER]", class_name, err)
                continue

            for fr in filtered_resources:
                res, err = r.remove(fr)
                print(region, class_name, res, err, fr)
                print()
            # results[region][class_name].append(fr)
            # print(f"{region} {class_name} Elapsed {time.time() - start_time:.2f}s")
            # print()
    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    ec2 = boto3.client("ec2")
    regions = get_regions(ec2)

    pool = futures.ThreadPoolExecutor(max_workers=len(regions))
    threads = []
    for region in regions:
        threads.append(pool.submit(work, resources.resources, region))

    futures.wait(threads)

    # pprint(results)
