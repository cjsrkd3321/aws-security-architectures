def detect_console_login(channel, detail, source_ips=[]):
    if detail["responseElements"]["ConsoleLogin"] != "Success":
        return

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
                            "text": f"*{detail['eventName']}* ({detail['awsRegion']})",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*시간:*\n{detail['eventTime']}"},
                            {
                                "type": "mrkdwn",
                                "text": f"*IP:*\n{detail['sourceIPAddress']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*계정:*\n{detail['recipientAccountId']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*종류:*\n{detail['userIdentity']['type']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*사용자:*\n{detail['userIdentity']['arn']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*MFA:*\n{detail['additionalEventData']['MFAUsed']}",
                            },
                        ],
                    },
                ],
            }
        ],
    }

    return slack_message
