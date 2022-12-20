import json
import logging
import os
import boto3

from libs.iam.console_login import detect_console_login
from libs.utils import send_message_to_slack

secrets = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.getenv("SECRET_ARN", "")
    )["SecretString"]
)

SLACK_HOOK_URL = secrets.get("slack_webhook_url", "")
SLACK_CHANNEL = secrets.get("slack_channel", "")
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

    if (
        source == "aws.signin"
        and detail_type == "AWS Console Sign In via CloudTrail"
        and detail["eventName"] == "ConsoleLogin"
    ):
        slack_message = detect_console_login(
            channel=SLACK_CHANNEL,
            detail=detail,
            source_ips=SOURCE_IPS,
        )

    if not slack_message:
        return

    send_message_to_slack(SLACK_HOOK_URL, slack_message)
