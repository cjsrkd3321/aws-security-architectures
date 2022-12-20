import hmac
import hashlib
import time
import requests

from urls import WRITE_URL

# https://api.slack.com/reference/block-kit/block-elements
APPROVED_SECTION = {"type": "section", "text": {"type": "mrkdwn", "text": "*APPROVED*"}}


def get_unlock_button(value):
    value = "UN" + value
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "UNLOCK",
                },
                "style": "primary",
                "value": value,
            }
        ],
    }


# https://api.slack.com/authentication/verifying-requests-from-slack
def verify_slack_signature(signing_secret, signature, ts, body):
    try:
        if abs(time.time() - int(ts)) > 60 * 5:
            return False
    except ValueError:
        return False

    base = bytes(f"v0:{ts}:", "utf-8") + body
    my_signature = "v0=" + hmac.new(signing_secret, base, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(my_signature, signature):
        return False
    return True


def send_exception(token, channel, ts, exception):
    res = requests.post(
        url=WRITE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-type": "application/json; charset=utf-8",
        },
        json={
            "channel": channel,
            "text": f"{exception}",
            "thread_ts": ts,
        },
    )
    print(res.json())


def is_approved(token, channel, ts, blocks, res_url, value):
    if value != "APPROVE":
        return False

    blocks.append(APPROVED_SECTION)
    res = requests.post(
        url=res_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-type": "application/json; charset=utf-8",
        },
        json={
            "channel": channel,
            "blocks": blocks,
            "ts": ts,
        },
    )
    print(res.json())
    return True


def send_thread_unlock_message(token, channel, ts, blocks, value):
    blocks.append(get_unlock_button(value))
    res = requests.post(
        url=WRITE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-type": "application/json; charset=utf-8",
        },
        json={
            "channel": channel,
            "blocks": blocks,
            "thread_ts": ts,
        },
    )
    print(res.json())
