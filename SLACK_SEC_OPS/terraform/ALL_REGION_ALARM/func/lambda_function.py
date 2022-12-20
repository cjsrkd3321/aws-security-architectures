import json
import logging
import os
import boto3

from libs.iam.console_login import detect_console_login
from libs.iam.create_access_key import detect_create_access_key
from libs.utils import send_message_to_slack

secrets = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.getenv("SECRET_ARN", "")
    )["SecretString"]
)

HOOK_URL = secrets.get("slack_webhook_url", "")
CHANNEL = secrets.get("slack_channel", "")
SOURCE_IPS = json.loads(os.getenv("SOURCE_IPS", "[]"))
SENSITIVE_PORTS = json.loads(os.getenv("SENSITIVE_PORTS", "[]"))
ALLOWED_IPS = json.loads(os.getenv("ALLOWED_IPS", "[]"))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print(type(event), event)
    [source, detail_type, detail] = [
        event["source"],
        event["detail-type"],
        event["detail"],
    ]

    region = detail["awsRegion"]

    if detail["eventName"] == "ConsoleLogin":
        slack_message = detect_console_login(CHANNEL, detail, region, SOURCE_IPS)
    elif detail["eventName"] == "CreateAccessKey":
        slack_message = detect_create_access_key(CHANNEL, detail, region, SOURCE_IPS)

    if not slack_message:
        return

    send_message_to_slack(HOOK_URL, slack_message)
