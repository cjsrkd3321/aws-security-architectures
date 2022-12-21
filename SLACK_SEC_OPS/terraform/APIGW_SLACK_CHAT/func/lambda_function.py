import base64
import boto3
import json
import os
import asyncio

from urllib import parse
from response import OK, BAD_REQUEST, UNAUTORIZED
from slacks import Slack
from libs import actors
from log import get_logs

secrets = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.getenv("SECRET_ARN", "")
    )["SecretString"]
)
REGIONS = [
    region.get("RegionName")
    for region in boto3.client("ec2").describe_regions()["Regions"]
]


SIGNING_SECRET = bytes(secrets.get("signing_secret", ""), "utf-8")
OAUTH_TOKEN = secrets.get("slack_oauth_token", "")
DENY_POLICY_ARN = os.getenv("DENY_POLICY_ARN")
MANAGER = os.getenv("MANAGER")


def lambda_handler(event, _):
    if not event.get("isBase64Encoded"):
        return BAD_REQUEST

    headers = event["headers"]
    body = base64.b64decode(event["body"])
    payload = json.loads(parse.unquote(str(body, "utf-8").split("=")[-1]))

    s = Slack(SIGNING_SECRET, OAUTH_TOKEN, headers, payload)
    if not s.verify_slack_signature(body):
        return UNAUTORIZED
    if s.user["username"] != MANAGER:
        return UNAUTORIZED

    try:
        if s.state.startswith("LOG|"):
            print(s.state)
            _, __, *filters = s.state.split("|")
            print(s.state)
            results = asyncio.run(get_logs(REGIONS, filters))
            s.send_thread(results)
            return OK

        if s.state == "APPROVE":
            s.send_approved()
            return OK

        act_type, region, evt, *args = s.state.split("|")
        actor = actors[evt](region, args, DENY_POLICY_ARN)

        if act_type == "BLOCK":
            actor.do(s.send_response, act_type)
        else:
            actor.undo(s.send_response, act_type)
    except Exception as e:
        s.send_thread(e)

    return OK
