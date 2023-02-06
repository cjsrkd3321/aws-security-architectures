import json
import logging
import os
import boto3

from libs.iam.console_login import detect_console_login
from libs.iam.create_access_key import detect_create_access_key
from libs.iam.deactivate_mfa_device import detect_deactivate_mfa_device
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
    msg = ""
    try:
        print(type(event), event)
        [source, detail_type, detail] = [
            event["source"],
            event["detail-type"],
            event["detail"],
        ]

        evt = detail["eventName"]
        region = detail["awsRegion"]

        if evt == "ConsoleLogin":
            msg = detect_console_login(CHANNEL, detail, region, SOURCE_IPS)
        elif evt == "CreateAccessKey":
            msg = detect_create_access_key(CHANNEL, detail, region, SOURCE_IPS)
        elif evt == "DeactivateMFADevice":
            msg = detect_deactivate_mfa_device(CHANNEL, detail, region, SOURCE_IPS)

        if not msg:
            return
        send_message_to_slack(HOOK_URL, msg)
    except Exception as e:
        send_message_to_slack(HOOK_URL, f"{region} {detail['eventID']} {evt} {e}")
