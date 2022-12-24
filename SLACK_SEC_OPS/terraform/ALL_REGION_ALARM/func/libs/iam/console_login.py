# https://docs.aws.amazon.com/ko_kr/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
# https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
def detect_console_login(channel, detail, region, source_ips=[]):
    if detail["responseElements"]["ConsoleLogin"] != "Success":
        return

    # IAMUser, AssumedRole, Root, SAMLUser, WebIdentityUser, AWSAccount
    user_type = (ui := detail["userIdentity"])["type"]
    role_name = ""
    if user_type == "AssumedRole":
        if "sessionContext" in ui:
            # AWS SSO etc...
            # arn:aws:iam::ACCOUNT_ID:role/rextest
            arn = ui["sessionContext"]["sessionIssuer"]["arn"]
            role_name = arn.split("/")[-1]
        else:
            # External SAML etc...
            # "arn:aws:sts::ACCOUNT_ID:assumed-role/rextest/admin"
            arn = ui["arn"]
            role_name = arn.split("/")[-2]
        user_name = ui["principalId"].split(":")[-1]
    elif user_type in ["Root", "IAMUser"]:
        arn = ui["arn"]
        user_name = ui.get("userName", "root")
    else:
        arn = "NEED_CHECK"
        user_name = "NEED_CHECK"
        print(detail["eventID"])

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
                            "text": f"*{detail['eventName']}* ({region})",
                        },
                    },
                    {
                        "type": "divider",
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
                                "text": f"*종류:*\n{user_type}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*사용자:*\n{arn}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*이름:*\n{user_name}",
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
                                    "text": "LOG(USER)",
                                },
                                "value": f"LOG|{region}|Username:{user_name}",
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
                                    "text": "BLOCK",
                                },
                                "style": "danger",
                                "value": f"BLOCK|{region}|ConsoleLogin|{user_name}|{role_name}",
                            },
                        ],
                    },
                ],
            }
        ],
    }
