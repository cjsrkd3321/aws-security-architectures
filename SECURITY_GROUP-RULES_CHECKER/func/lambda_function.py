import os
import csv
import boto3

from datetime import date, timedelta, datetime
from utils import *

from EC2 import EC2
from Query import Query
from Athena import Athena

TODAY = str(date.today()).replace("-", "/")
YESTERDAY = str(date.today() - timedelta(days=1)).replace("-", "/")

ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
TABLE = "vflt"
VPC_FLOW_LOG_BUCKET = os.getenv("VPC_FLOW_LOG_BUCKET", "")
WORKGROUP = os.getenv("WORKGROUP", "vpcflowlogs")
CSV_PATH = "/tmp/res.csv"


# https://stackoverflow.com/questions/72313845/multiprocessing-picklingerror-cant-pickle-class-botocore-client-s3-attr
def check_sgr(service, result):
    sgr_id = result["sgr_id"]
    protocol = result["protocol"]
    dst_ports = combine_ports(result["from_port"], result["to_port"])
    ec2 = boto3.client(service)

    detected_at = [tag for tag in result["tags"] if tag["Key"] == "DetectedAt"]
    if not detected_at:
        ec2.create_tags(
            Resources=[sgr_id],
            Tags=[{"Key": "DetectedAt", "Value": f"{TODAY}"}],
        )

    fp = open(CSV_PATH)
    lines = (line for line in csv.reader(fp))
    next(lines)  # 메뉴 제거
    for line in lines:
        proto, port, src, dst = line
        if (int(proto) > int(protocols[protocol])) or (int(port) > max(dst_ports)):
            return

        if not is_equal_protocol(proto, protocol):
            continue

        if not is_included_port(port, dst_ports):
            continue

        if not is_included_ip(src, result["src_ips"]):
            continue

        if not is_included_ip(dst, result["dst_ips"]):
            continue

        ec2.create_tags(
            Resources=[sgr_id], Tags=[{"Key": "LastUsedAt", "Value": f"{TODAY}"}]
        )
        break


def lambda_handler(event, _):
    # EventBridge
    if "Records" not in event:
        q = Query(
            account_id=ACCOUNT_ID,
            bucket=VPC_FLOW_LOG_BUCKET,
            table=TABLE,
            region="ap-northeast-2",
            date=TODAY,
        )  # YESTERDAY
        a = Athena(boto3.client("athena"), WORKGROUP)
        if not a.is_table_exists(TABLE):
            a.run_query(q.vpc_flow_log_table_query)
        a.run_query(q.vpc_flow_log_query)
        return
    # S3 event notification (query results)
    else:
        bucket, object = (s3 := event["Records"][0]["s3"])["bucket"], s3["object"]
        boto3.client("s3").download_file(bucket["name"], object["key"], CSV_PATH)

        e = EC2(boto3.client("ec2"))
        results = []
        sgrs, nis = e.security_group_rules, e.network_interfaces
        for sgr in sgrs:
            sg_id, sgr_id = sgr["GroupId"], sgr["SecurityGroupRuleId"]

            if not e.is_ingress_rule(sgr):
                continue

            src_ips = (
                [cidr_ip]
                if (cidr_ip := sgr.get("CidrIpv4"))
                else e.get_private_ips_using_sg_id(
                    sgr.get("ReferencedGroupInfo", {}).get("GroupId"), nis
                )
            )
            dst_ips = e.get_private_ips_using_sg_id(sg_id, nis)
            if src_ips == dst_ips:  # continue if src equals dst
                continue

            results.append(
                {
                    "sg_id": sg_id,
                    "sgr_id": sgr_id,
                    "src_ips": src_ips,
                    "dst_ips": dst_ips,
                    "protocol": sgr["IpProtocol"],
                    "from_port": sgr["FromPort"],
                    "to_port": sgr["ToPort"],
                    "tags": sgr["Tags"],
                }
            )

        try:
            run_multi_processes(check_sgr, "ec2", results)
        except Exception as e:
            print(e)

        os.remove(CSV_PATH)

        # Print results
        sgrs = e.security_group_rules
        for sgr in sgrs:
            if not e.is_ingress_rule(sgr):
                continue

            last_used_at = EC2.get_tag_value(sgr["Tags"], "LastUsedAt")
            detected_at = EC2.get_tag_value(sgr["Tags"], "DetectedAt")
            if not (last_used_at or detected_at):
                print(sgr["GroupId"], sgr["SecurityGroupRuleId"], sgr["Tags"], "UNUSED")
            else:
                print(
                    sgr["GroupId"],
                    sgr["SecurityGroupRuleId"],
                    sgr["Tags"],
                    (
                        datetime.strptime(TODAY, "%Y/%m/%d")
                        - datetime.strptime(detected_at, "%Y/%m/%d")
                    ).days
                    if not last_used_at
                    else (
                        datetime.strptime(TODAY, "%Y/%m/%d")
                        - datetime.strptime(last_used_at, "%Y/%m/%d")
                    ).days,
                )
        return


if __name__ == "__main__":
    lambda_handler("", "")
