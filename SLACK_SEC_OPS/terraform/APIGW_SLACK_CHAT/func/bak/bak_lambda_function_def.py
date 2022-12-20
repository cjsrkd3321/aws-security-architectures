import base64
import boto3
import json
import os

from urllib import parse
from response import OK, BAD_REQUEST, UNAUTORIZED
from slacks import (
    verify_slack_signature,
    send_exception,
    is_approved,
    send_thread_unlock_message,
)
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

    try:
        headers = event["headers"]
        signature = headers.get("x-slack-signature", "")
        timestamp = headers.get("x-slack-request-timestamp", "0")
        body = base64.b64decode(event["body"])

        if not verify_slack_signature(SIGNING_SECRET, signature, timestamp, body):
            return UNAUTORIZED

        # Parse some values for sending slack message
        payload = json.loads(parse.unquote(str(body, "utf-8").split("=")[-1]))
        msg_ts = (msg := payload["message"])["ts"]
        channel = payload["channel"]["id"]
        blocks = (
            msg["attachments"][0]["blocks"][:-1]
            if "attachments" in msg
            else msg["blocks"][:-1]
        )
        response_url = payload["response_url"]
        user_id, user_name, team_id = (
            (user := payload["user"])["id"],
            user["username"],
            user["team_id"],
        )
        print(user_id, user_name, channel, team_id, msg_ts, channel)

        value = payload["actions"][0]["value"]
        if is_approved(OAUTH_TOKEN, channel, msg_ts, blocks, response_url, value):
            return OK

        lock_type, evt, *args = value.split("|")

        if evt == "ConsoleLogin":
            console_login(lock_type, args, DENY_POLICY_ARN)

        if lock_type == "ACTION":
            send_thread_unlock_message(OAUTH_TOKEN, channel, msg_ts, blocks, value)
    except Exception as e:
        send_exception(OAUTH_TOKEN, channel, msg_ts, e)

    return OK
