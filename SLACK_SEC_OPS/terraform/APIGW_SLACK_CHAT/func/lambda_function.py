import base64
import boto3
import json
import os

from urllib import parse
from response import OK, BAD_REQUEST, UNAUTORIZED
from slacks import Slack
from libs.iam.ConsoleLogin import console_login

secrets = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.getenv("SECRET_ARN", "")
    )["SecretString"]
)


SIGNING_SECRET = bytes(secrets.get("signing_secret", ""), "utf-8")
OAUTH_TOKEN = secrets.get("slack_oauth_token", "")
DENY_POLICY_ARN = os.getenv("DENY_POLICY_ARN")


def lambda_handler(event, _):
    if not event.get("isBase64Encoded"):
        return BAD_REQUEST

    headers = event["headers"]
    body = base64.b64decode(event["body"])
    payload = json.loads(parse.unquote(str(body, "utf-8").split("=")[-1]))

    s = Slack(SIGNING_SECRET, OAUTH_TOKEN, headers, payload)
    if not s.verify_slack_signature(body):
        return UNAUTORIZED
    print(s.user)

    try:
        if s.state == "APPROVE":
            s.send_approved()
        else:
            lock_type, evt, *args = s.state.split("|")
            if evt == "ConsoleLogin":
                console_login(lock_type, args, DENY_POLICY_ARN)

            if lock_type == "ACTION":
                s.send_thread_unlock()
    except Exception as e:
        s.send_exception(e)

    return OK
