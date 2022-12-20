from datetime import datetime


def get_button(text, value):
    print(f"[get_lock_button] {value}")
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": f"{text}",
                },
                "style": "danger",
                "value": f"{text}|{'|'.join(value.split('|')[1:])}",
            }
        ],
    }


def get_text_section(text):
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*{text}* {datetime.now()}"},
    }
