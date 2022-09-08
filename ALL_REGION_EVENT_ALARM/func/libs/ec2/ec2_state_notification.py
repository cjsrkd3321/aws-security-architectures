def detect_ec2_state_notification(channel, detail):
    slack_message = {
        "channel": channel,
        "text": str(detail),
    }

    return slack_message
