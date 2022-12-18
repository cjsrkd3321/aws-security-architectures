import base64
import boto3
import json
import os

from response import OK, BAD_REQUEST, UNAUTORIZED
from utils import verify_slack_signature

secrets = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.getenv("SECRET_ARN", "")
    )["SecretString"]
)

SIGNING_SECRET = bytes(secrets.get("signing_secret", ""), "utf-8")
OAUTH_TOKEN = secrets.get("slack_oauth_token", "")


def lambda_handler(event, _):
    if not event.get("isBase64Encoded"):
        return BAD_REQUEST

    headers = event["headers"]
    signature = headers.get("x-slack-signature", "")
    timestamp = headers.get("x-slack-request-timestamp", "0")
    body = base64.b64decode(event["body"])

    if not verify_slack_signature(SIGNING_SECRET, signature, timestamp, body):
        return UNAUTORIZED

    return OK
