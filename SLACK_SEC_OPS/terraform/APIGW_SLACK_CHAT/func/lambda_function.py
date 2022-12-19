import base64
import boto3
import json
import os
import requests

from urllib import parse
from response import OK, BAD_REQUEST, UNAUTORIZED
from urls import WRITE_URL
from utils import verify_slack_signature

secrets = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.getenv("SECRET_ARN", "")
    )["SecretString"]
)
iam = boto3.client("iam")

SIGNING_SECRET = bytes(secrets.get("signing_secret", ""), "utf-8")
OAUTH_TOKEN = secrets.get("slack_oauth_token", "")
DENY_POLICY_ARN = os.getenv("DENY_POLICY_ARN")


def lambda_handler(event, _):
    if not event.get("isBase64Encoded"):
        return BAD_REQUEST

    try:
        headers = event["headers"]
        signature = headers.get("x-slack-signature", "")
        timestamp = headers.get("x-slack-request-timestamp", "0")
        body = base64.b64decode(event["body"])

        if not verify_slack_signature(SIGNING_SECRET, signature, timestamp, body):
            return UNAUTORIZED

        payload = json.loads(parse.unquote(str(body, "utf-8").split("=")[-1]))
        msg_ts = payload["message"]["ts"]
        channel = payload["channel"]["id"]
        blocks = payload["message"]["attachments"][0]["blocks"][:-1]
        response_url = payload["response_url"]
        user_id, user_name, team_id = (
            (user := payload["user"])["id"],
            user["username"],
            user["team_id"],
        )
        print(user_id, user_name, team_id, msg_ts, channel)

        value = payload["actions"][0]["value"]
        if value == "APPROVE":
            blocks.append(
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "APPROVED",
                    },
                },
            )
            res = requests.post(
                url=response_url,
                headers={
                    "Authorization": f"Bearer {OAUTH_TOKEN}",
                    "Content-type": "application/json; charset=utf-8",
                },
                json={
                    "channel": channel,
                    "blocks": blocks,
                    "ts": msg_ts,
                },
            )
            print(res.json())
            return OK

        evt, *args = value.split("|")

        if evt == "ConsoleLogin":
            user_name, role_name = args
            if user_name == "root" or role_name.startswith("AWSReservedSSO_"):
                return OK
            if role_name:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=DENY_POLICY_ARN)
            else:
                iam.attach_user_policy(UserName=user_name, PolicyArn=DENY_POLICY_ARN)
    except Exception as e:
        res = requests.post(
            url=WRITE_URL,
            headers={
                "Authorization": f"Bearer {OAUTH_TOKEN}",
                "Content-type": "application/json; charset=utf-8",
            },
            json={
                "channel": channel,
                "text": f"{e}",
                "thread_ts": msg_ts,
            },
        )
        print(res.json())

    return OK
