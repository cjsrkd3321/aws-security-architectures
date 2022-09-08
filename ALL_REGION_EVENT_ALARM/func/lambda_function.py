import json
import logging
import os

from libs.iam.console_login import detect_console_login
from libs.iam.create_access_key import detect_create_access_key
from libs.ec2.sensitive_port_open import detect_sensitive_port_open
from libs.ec2.ec2_state_notification import detect_ec2_state_notification
from libs.utils import send_message_to_slack


SLACK_HOOK_URL = os.environ["SLACK_HOOK_URL"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
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
    elif (
        source == "aws.iam"
        and detail_type == "AWS API Call via CloudTrail"
        and detail["eventName"] == "CreateAccessKey"
    ):
        slack_message = detect_create_access_key(
            channel=SLACK_CHANNEL,
            detail=detail,
            source_ips=SOURCE_IPS,
        )
    elif (
        source == "aws.ec2"
        and detail_type == "AWS API Call via CloudTrail"
        and detail["eventName"]
        in ["AuthorizeSecurityGroupIngress", "ModifySecurityGroupRules"]
    ):
        slack_message = detect_sensitive_port_open(
            channel=SLACK_CHANNEL,
            detail=detail,
            sensitive_ports=SENSITIVE_PORTS,
            allowed_ips=ALLOWED_IPS,
        )
    elif (
        source == "aws.ec2" and detail_type == "EC2 Instance State-change Notification"
    ):
        slack_message = detect_ec2_state_notification(
            channel=SLACK_CHANNEL,
            detail=detail,
        )

    if not slack_message:
        return

    send_message_to_slack(SLACK_HOOK_URL, slack_message)
