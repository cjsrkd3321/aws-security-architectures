def detect_console_login(channel, detail, source_ips=[]):
    res = detail["responseElements"]
    add_event_data = detail["additionalEventData"]
    evt = detail["eventName"]
    if "Success" != res.get("ConsoleLogin"):
        return

    if evt == "SwitchRole" and "SwitchFrom" not in add_event_data:
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
                            "text": f"*{evt}* ({detail['awsRegion']})",
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
                                "text": f"*MFA:*\n{add_event_data.get('MFAUsed')}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*SWITCH_FROM:*\n{add_event_data.get('SwitchFrom')}",
                            },
                        ],
                    },
                ],
            }
        ],
    }

    return slack_message
