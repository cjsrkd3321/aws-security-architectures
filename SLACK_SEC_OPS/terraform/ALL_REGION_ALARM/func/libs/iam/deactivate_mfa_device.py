def detect_deactivate_mfa_device(channel, detail, region, source_ips=[]):
    event_time = detail["eventTime"]
    access_key = detail["userIdentity"]["accessKeyId"]
    event_name = detail["eventName"]
    ip = detail["sourceIPAddress"]
    rp = detail["requestParameters"]

    # Root 엑세스 키는 UserName이 존재하지 않음(계정별칭을 추가하면 생김)
    target_user = rp.get("userName", "root")
    serial_number = rp["serialNumber"]
    arn = detail["userIdentity"]["arn"]

    return {
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
                                "text": f"*행위자:*\n{arn}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*행위자키:*\n`{access_key}`",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*대상자:*\n{target_user}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*시리얼:*\n{serial_number}",
                            },
                        ],
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "LOG(행위자)",
                                },
                                "value": f"LOG|{region}|AccessKeyId:{access_key}",
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "LOG(대상자)",
                                },
                                "value": f"LOG|{region}|Username:{target_user}",
                            },
                        ],
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "APPROVE",
                                },
                                "style": "primary",
                                "value": f"APPROVE",
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "BLOCK(대상자)",
                                },
                                "style": "danger",
                                "value": f"BLOCK|{region}|DeactivateMFADevice|{target_user}|",
                            },
                        ],
                    },
                ],
            }
        ],
    }
