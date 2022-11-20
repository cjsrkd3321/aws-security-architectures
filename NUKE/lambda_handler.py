from pprint import pprint
from typing import Optional, List, Callable, Dict
from concurrent import futures
from resources._utils import filter_func

import boto3
import resources


results: Dict = {}


def get_regions(ec2) -> List[Optional[str]]:
    return [region.get("RegionName") for region in ec2.describe_regions()["Regions"]]


def work(resources: List[Callable], region):
    if region == "ap-northeast-2":
        return

    try:
        global results
        results[region] = {}
        for resource in resources:
            r = resource(region=region)

            class_name = r.__class__.__name__
            if class_name.startswith("IAM") and region != "us-east-1":
                continue

            results[region][class_name] = []

            rs = r.list()
            # print(class_name, rs)
            if type(rs) == str:
                print(class_name, rs)
                continue
            filtered_resources = r.filter(rs, filter_func)
            # print(filtered_resources)
            for fr in filtered_resources:
                results[region][class_name].append(fr)
                print(region, class_name, fr, r.remove(fr))
                print()
    except:
        import traceback

        print(traceback.format_exc())
        pass


if __name__ == "__main__":
    ec2 = boto3.client("ec2")
    regions = get_regions(ec2)

    # regions = ["us-east-1"]
    pool = futures.ThreadPoolExecutor(max_workers=len(regions))
    threads = []
    for region in regions:
        threads.append(pool.submit(work, resources.resources, region))

    futures.wait(threads)

    pprint(results)
