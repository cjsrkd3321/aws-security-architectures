class Query:
    def __init__(self, account_id, bucket, table, region, date):
        self.account_id = account_id
        self.bucket = bucket
        self.table = table
        self.region = region
        self.date = date

    @property
    def vpc_flow_log_table_query(self):
        return f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {self.table} (
                `flow_direction` string, 
                `protocol` bigint, 
                `srcaddr` string, 
                `dstaddr` string, 
                `dstport` int, 
                `action` string, 
                `log_status` string, 
                `tcp_flags` int, 
                `type` string, 
                `start` bigint, 
                `end` bigint
            )
            PARTITIONED BY (region string, day string)
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ' '
            LOCATION 's3://{self.bucket}/AWSLogs/{self.account_id}/vpcflowlogs/'
            TBLPROPERTIES
            (
                "skip.header.line.count"="1",
                "projection.enabled" = "true",
                "projection.region.type" = "enum",
                "projection.region.values" = "ap-northeast-2",
                "projection.day.type" = "date",
                "projection.day.range" = "2022/01/01,NOW",
                "projection.day.format" = "yyyy/MM/dd",
                "storage.location.template" = "s3://{self.bucket}/AWSLogs/{self.account_id}/vpcflowlogs/${{region}}/${{day}}"
            )
        """

    @property
    def vpc_flow_log_query(self):
        return f"""
            SELECT distinct protocol, dstport, srcaddr, dstaddr 
            FROM {self.table} 
            WHERE 
                flow_direction = 'ingress' 
                AND action = 'ACCEPT' 
                AND day = '{self.date}' 
                AND region = '{self.region}'
                AND type = 'IPv4' 
                AND (
                        protocol = 6 
                    OR 
                        protocol = 17
                )
            ORDER BY protocol, dstport
        """
