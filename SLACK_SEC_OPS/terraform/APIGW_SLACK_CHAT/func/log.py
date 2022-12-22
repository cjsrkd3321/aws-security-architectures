import asyncio
import boto3
import json

from datetime import datetime, timedelta
from botocore.config import Config


async def get_logs(regions=["ap-northeast-1", "us-east-1"], filters=[]):
    results = []
    logs = ""
    done, _ = await asyncio.wait(
        [asyncio.create_task(lookup_events(region, filters)) for region in regions]
    )
    for d in done:
        results += d.result()

    results = sorted(results, key=lambda x: x[3])  # by eventTime
    for result in results:
        logs += " ".join(result) + "\n"
    return logs


async def lookup_events(region="ap-northeast-1", filters=[]):
    NOW = datetime.now()
    SEARCH_TIME_RANGE = timedelta(hours=10)  # exactly 1 hour in Korea
    logs = []

    attrs = [
        {"AttributeKey": f.split(":")[0], "AttributeValue": f.split(":")[1]}
        for f in filters
    ]
    trail = boto3.client("cloudtrail", config=Config(region_name=region))
    try:
        iterator = trail.get_paginator("lookup_events").paginate(
            LookupAttributes=attrs,
            StartTime=(NOW - SEARCH_TIME_RANGE),
            EndTime=NOW,
        )
    except Exception as exc:
        return [[region, exc]]

    events = [
        json.loads(e["CloudTrailEvent"])
        for events in iterator
        for e in events["Events"]
    ]
    for e in events:
        if not (err := e.get("errorCode", "")) and e["readOnly"]:
            continue
        console = "CO" if e.get("sessionCredentialFromConsole") else "API"
        logs.append(
            [
                f"*{console}*",
                e["recipientAccountId"],
                e["awsRegion"],
                e["eventTime"],
                f"*{e['sourceIPAddress']}*",
                e["eventName"],
                f"*{err}*",
            ]
        )

    return logs
