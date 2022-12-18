from flask import Flask, request, make_response
from pprint import pprint

import hmac
import hashlib
import time
import json
import requests

# https://api.slack.com/authentication/verifying-requests-from-slack
# 토큰 검증 방법

TOKEN = ""
SIGNING_SECRET = bytes("", "utf-8")

app = Flask(__name__)


# https://api.slack.com/authentication/verifying-requests-from-slack
@app.before_request
def verify_slack_signature():
    FORBIDDEN = make_response("Unauthorized", 403)
    slack_signature = request.headers.get("X-Slack-Signature", "")
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "0")
    body = request.get_data()

    try:
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return FORBIDDEN
    except ValueError:
        return FORBIDDEN

    base = bytes(f"v0:{timestamp}:", "utf-8") + body
    my_signature = "v0=" + hmac.new(SIGNING_SECRET, base, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(my_signature, slack_signature):
        return FORBIDDEN


# https://api.slack.com/interactivity/handling#acknowledgment_response
@app.route("/", methods=["POST"])
def index():
    OK = make_response("OK", 200)
    # print(request.headers)
    print(request.headers["X-Forwarded-For"])
    try:
        payload = json.loads(request.form["payload"])
    except Exception as e:
        return

    print(payload["actions"])
    res_url = payload["response_url"]

    # https://api.slack.com/interactivity/handling#message_responses
    res = requests.post(
        # url="https://slack.com/api/chat.update",
        url="https://slack.com/api/chat.postMessage",
        # url=res_url,
        headers={
            # https://api.slack.com/apps/A04E8S08DE3/oauth?
            "Authorization": f"Bearer {TOKEN}",
            "Content-type": "application/json; charset=utf-8",
        },
        json={
            "channel": payload["channel"]["id"],
            "blocks": payload["message"]["blocks"][:-1],
            # "ts": payload["message"]["ts"],
            "thread_ts": payload["message"]["ts"],
        },
    )
    # print(res.json())

    print(payload["channel"]["id"], payload["message"]["ts"])

    # https://api.slack.com/interactivity/handling#acknowledgment_response
    return OK


if __name__ == "__main__":
    app.run(port=8080, debug=True)
