import os
import base64, gzip
import uuid
import json
import boto3
import logging
from datetime import date
from botocore.config import Config
from libs.ec2 import get_running_instances, get_available_regions
from libs.macie2 import get_detect_result_from_sensitive_result
from libs.utils import send_message_to_slack, get_slack_message, jsonb_gzip_to_jsons


logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_HOOK_URL = os.environ["SLACK_HOOK_URL"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
SNS_ASSUME_ROLE_ARN = os.getenv("SNS_ASSUME_ROLE_ARN")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
PRIAVTE_INFO_BUCKET = os.getenv("PRIAVTE_INFO_BUCKET")
RESULT_BUCKET = os.getenv("RESULT_BUCKET")
S3_ACCOUNT_ID = os.getenv("S3_ACCOUNT_ID")
EVENTBRIDGE_WARM_ARN = os.getenv("EVENTBRIDGE_WARM_ARN")

s3 = boto3.client("s3", config=Config(region_name="us-east-1"))
macie2 = boto3.client("macie2", config=Config(region_name="us-east-1"))

COMMAND_COMPLETED_REGIONS = []


def lambda_handler(event, context):
    global COMMAND_COMPLETED_REGIONS

    today = date.today().isoformat()
    uuid_v4 = uuid.uuid4().hex
    detect_results = []
    csv_data = "CATEGORY,TYPE,OBJECT,VALUE\n"
    private_info_bucket_name = PRIAVTE_INFO_BUCKET.split(":")[-1]
    result_bucket_name = RESULT_BUCKET.split(":")[-1]

    ################################################################
    # FOR WARMING CONDITION
    ################################################################
    if "resources" in event and EVENTBRIDGE_WARM_ARN in event["resources"][0]:
        return

    # https://docs.aws.amazon.com/ko_kr/macie/latest/user/discovery-jobs-monitor-cw-logs.html
    # { "awslogs": {"data": "BASE64ENCODED_GZIP_COMPRESSED_DATA"} }
    ################################################################
    # COMPLETED CLASSIFICATION JOB (LAST)
    ################################################################
    if "awslogs" in event:
        send_message_to_slack(
            hook_url=SLACK_HOOK_URL,
            slack_message=get_slack_message(
                slack_channel=SLACK_CHANNEL,
                message=f"*MACIE JOB ENDED AND PARSING STARTED*",
            ),
        )

        encoded_data = event["awslogs"]["data"]
        job_id = json.loads(
            json.loads(gzip.decompress(base64.b64decode(encoded_data)))["logEvents"][0][
                "message"
            ]
        )["jobId"]

        next_token = ""
        all_finding_ids = []
        while True:
            res = macie2.list_findings(
                findingCriteria={
                    "criterion": {
                        # https://docs.aws.amazon.com/ko_kr/macie/latest/user/findings-filter-fields.html
                        "classificationDetails.jobId": {
                            "eq": [job_id],
                        }
                    }
                },
                maxResults=50,
                nextToken=next_token,
            )
            all_finding_ids += res["findingIds"]
            next_token = res.get("nextToken")
            if not next_token:
                break

        findings = macie2.get_findings(
            findingIds=all_finding_ids,
        )["findings"]

        # https://docs.aws.amazon.com/ko_kr/macie/latest/APIReference/findings-describe.html
        details = [
            (finding["classificationDetails"], finding["resourcesAffected"])
            for finding in findings
            if finding["category"] == "CLASSIFICATION"  # ["POLICY", "CLASSIFICATION"]
        ]

        for detail, resource in details:
            detailed_reults_location = detail["detailedResultsLocation"]
            result = detail["result"]
            # ["COMPLETE", "PARTIAL", "SKIPPED"]
            if result["status"]["code"] == "SKIPPED":
                continue

            # private-info-bucket-xzqgh75p/i-04b6f16d916efd901/etc/ssh/ssh_host_ed25519_key
            affected_object_path = resource["s3Object"]["path"]

            # 추후 구현 필요
            if result["additionalOccurrences"]:
                # i-04b6f16d916efd901/etc/ssh/ssh_host_ed25519_key
                file_path = resource["s3Object"]["key"]
                # Split after delete s3://
                splited_location = detailed_reults_location[5:].split("/")
                bucket_name, key = [splited_location[0], "/".join(splited_location[1:])]
                body = s3.get_object(
                    Bucket=bucket_name,
                    Key=key,
                )["Body"].read()
                jsons = jsonb_gzip_to_jsons(body)
                for json_ in jsons:
                    if file_path != json_["resourcesAffected"]["s3Object"]["key"]:
                        continue
                    additional_result = json_["classificationDetails"]["result"]
                    detect_results += get_detect_result_from_sensitive_result(s3, affected_object_path, additional_result)
            else:
                detect_results += get_detect_result_from_sensitive_result(s3, affected_object_path, result)
                
        # Convert detect_results to CSV format
        for detect_result in detect_results:
            for result_key, result_values in detect_result.items():
                [type_, category, object] = result_key.split("|")
                for result_value in result_values:
                    csv_data += f"{type_},{category},{object},{result_value}\n"

        s3.put_object(
            Bucket=result_bucket_name,
            Body=csv_data,
            Key=f"{today}-private-info-detect-results-{uuid_v4}.csv",
        )

        send_message_to_slack(
            hook_url=SLACK_HOOK_URL,
            slack_message=get_slack_message(
                slack_channel=SLACK_CHANNEL,
                message=f"*MACIE PARSING ENDED (<https://s3.console.aws.amazon.com/s3/buckets/{result_bucket_name}|Bucket Link>)*",
            ),
        )

        return

    # https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/monitoring-sns-examples.html
    # Refer to sns-event.json file
    ################################################################
    # RUN COMMAND ENDED & CREATE CLASSIFICATION JOB (SECOND)
    ################################################################
    elif "Records" in event:
        # If not exist COMMAND_COMPLETED_REGIONS, Do not run
        if not COMMAND_COMPLETED_REGIONS:
            send_message_to_slack(
                hook_url=SLACK_HOOK_URL,
                slack_message=get_slack_message(
                    slack_channel=SLACK_CHANNEL,
                    message=f"*MACIE LAMBDA SOMETHING WRONG. NO REGIONS*",
                    is_succeeded=False,
                ),
            )
            return

        sns_message = event["Records"][0]["Sns"]
        sns_region = sns_message["Subject"].split(" ")[-1]
        command_status = json.loads(sns_message["Message"])["status"]

        COMMAND_COMPLETED_REGIONS.remove(sns_region)

        send_message_to_slack(
            hook_url=SLACK_HOOK_URL,
            slack_message=get_slack_message(
                slack_channel=SLACK_CHANNEL,
                message=f"*MACIE RUN COMMAND ENDED* ({command_status}) ({sns_region})",
                is_succeeded=(command_status == "Success"),
            ),
        )

        if len(COMMAND_COMPLETED_REGIONS) == 0 and command_status == "Success":
            job_name = f"{today}-{uuid_v4}"
            custom_identifiers = macie2.list_custom_data_identifiers()["items"]
            custom_identifier_ids = [
                custom_identifier["id"] for custom_identifier in custom_identifiers
            ]

            job_id = macie2.create_classification_job(
                customDataIdentifierIds=custom_identifier_ids,
                clientToken=job_name,
                jobType="ONE_TIME",
                managedDataIdentifierSelector="ALL",
                name=job_name,
                s3JobDefinition={
                    "bucketDefinitions": [
                        {
                            "accountId": S3_ACCOUNT_ID,
                            "buckets": [private_info_bucket_name],
                        }
                    ]
                },
            )["jobId"]

            send_message_to_slack(
                hook_url=SLACK_HOOK_URL,
                slack_message=get_slack_message(
                    slack_channel=SLACK_CHANNEL,
                    message=f"*MACIE INSPECTION JOB STARTED* ({job_id})",
                ),
            )

        return
    
    ################################################################
    # INITIAL EXECUTION (FIRST)
    ################################################################
    else:
        COMMAND_COMPLETED_REGIONS = []
        for region in get_available_regions():
            ec2 = boto3.client("ec2", config=Config(region_name=region))
            ssm = boto3.client("ssm", config=Config(region_name=region))
            ssm_connected_instances = []

            for instance in get_running_instances(ec2):
                status = ssm.get_connection_status(Target=instance["InstanceId"])["Status"]
                if status == "connected":
                    ssm_connected_instances.append(instance["InstanceId"])

            if not ssm_connected_instances:
                continue

            sns_arn = f"arn:aws:sns:{region}:{S3_ACCOUNT_ID}:{SNS_TOPIC_ARN.split(':')[-1]}"
            command_id = ssm.send_command(
                InstanceIds=ssm_connected_instances,
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        "INSTANCE_ID=`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`",
                        'find / -type f -mtime -1 ! -executable ! -size 0 ! -path "/proc/*" ! -path "/sys/*" ! -path "/run/*" ! -path "/var/log/dmesg" -exec aws s3 cp {} s3://'
                        + private_info_bucket_name
                        + "/$INSTANCE_ID{} \; 2> /dev/null",
                        "exit 0",
                    ]
                },
                TimeoutSeconds=600,
                MaxConcurrency="1000000",
                ServiceRoleArn=SNS_ASSUME_ROLE_ARN,
                NotificationConfig={
                    "NotificationArn": sns_arn,
                    "NotificationEvents": ["Success", "TimedOut", "Cancelled", "Failed"],
                    "NotificationType": "Command",
                },
            )["Command"]["CommandId"]

            COMMAND_COMPLETED_REGIONS.append(region)

            send_message_to_slack(
                hook_url=SLACK_HOOK_URL,
                slack_message=get_slack_message(
                    slack_channel=SLACK_CHANNEL,
                    message=f"*MACIE RUN COMMAND START* ({command_id}) ({region})",
                ),
            )
