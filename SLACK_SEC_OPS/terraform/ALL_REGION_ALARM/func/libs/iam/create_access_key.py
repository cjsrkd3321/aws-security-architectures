def detect_create_access_key(channel, detail, source_ips=[]):
    event_time = detail["eventTime"]
    arn = detail["userIdentity"]["arn"]
    access_key = detail["userIdentity"]["accessKeyId"]

    event_name = detail["eventName"]
    region = detail["awsRegion"]
    ip = detail["sourceIPAddress"]

    created_access_key_info = detail["responseElements"]["accessKey"]

    # Root 엑세스 키는 UserName이 존재하지 않음(조직으로 묶이면 달라질 수 있음)
    user_name = created_access_key_info.get("userName", "")
    created_access_key_id = created_access_key_info["accessKeyId"]

    slack_message = {
        "channel": channel,
        "attachments": [
            {
                "color": "#30db3f"
                if detail["sourceIPAddress"] in source_ips
                else "#eb4034",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{event_name}* ({region})",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*시간:*\n{event_time}"},
                            {
                                "type": "mrkdwn",
                                "text": f"*IP:*\n{ip}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*계정:*\n{detail['recipientAccountId']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*발급인:*\n{arn}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*발급인키:*\n`{access_key}`",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*사용자:*\n{user_name}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Access Key ID:*\n{created_access_key_id}",
                            },
                        ],
                    },
                ],
            }
        ],
    }

    return slack_message
