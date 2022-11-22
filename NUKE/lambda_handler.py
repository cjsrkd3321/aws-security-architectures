from pprint import pprint
from typing import Optional, List, Callable, Dict
from concurrent import futures
from resources._utils import filter_func

import time
import boto3
import resources


results: Dict = {}


def get_regions(ec2) -> List[Optional[str]]:
    return [region.get("RegionName") for region in ec2.describe_regions()["Regions"]]


def work(resources: List[Callable], region):
    if region not in ["ap-northeast-2", "us-east-1"]:
        return

    try:
        global results
        results[region] = {}
        for resource in resources:
            start_time = time.time()
            r = resource(region=region)

            class_name = r.__class__.__name__
            if class_name.startswith("IAM") and region != "us-east-1":
                continue

            results[region][class_name] = []

            rs, err = r.list()
            if err:
                print("[ERR_LIST]", class_name, err)
                continue

            filtered_resources, err = r.filter(rs, filter_func)
            if err:
                print("[ERR_FILTER]", class_name, err)
                continue

            for fr in filtered_resources:
                results[region][class_name].append(fr)
            print(f"{region} {class_name} Elapsed {time.time() - start_time:.2f}s")
    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    ec2 = boto3.client("ec2")
    regions = get_regions(ec2)

    # regions = ["ap-northeast-2"]
    pool = futures.ThreadPoolExecutor(max_workers=len(regions))
    threads = []
    for region in regions:
        threads.append(pool.submit(work, resources.resources, region))

    futures.wait(threads)

    # pprint(results)
