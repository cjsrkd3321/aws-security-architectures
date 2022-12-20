import requests
import hmac
import time

from hashlib import sha256
from urls import WRITE_URL
from utils import get_button, get_text_section

APPROVED_SECTION = {"type": "section", "text": {"type": "mrkdwn", "text": "*APPROVED*"}}


class Slack:
    def __init__(self, signing_secret, token, headers, payload):
        self.signing_secret = signing_secret
        self.token = token
        self.signature = headers.get("x-slack-signature", "")
        self.sig_ts = headers.get("x-slack-request-timestamp", "0")
        self.channel = payload["channel"]["id"]
        self.response_url = payload["response_url"]
        self.msg_ts = payload["message"]["ts"]
        self.blocks = (
            payload["message"]["attachments"][0]["blocks"][:-1]
            if "attachments" in payload["message"]
            else payload["message"]["blocks"][:-1]
        )
        self.value = payload["actions"][0]["value"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-type": "application/json; charset=utf-8",
        }
        self._user = payload["user"]

    def verify_slack_signature(self, body):
        try:
            if abs(time.time() - int(self.sig_ts)) > 60 * 5:
                return False
        except ValueError:
            return False

        base = bytes(f"v0:{self.sig_ts}:", "utf-8") + body
        my_sign = "v0=" + hmac.new(self.signing_secret, base, sha256).hexdigest()
        if not hmac.compare_digest(my_sign, self.signature):
            return False
        return True

    def send_response(self, text):
        if text == "BLOCK":
            button = get_button("UNBLOCK", self.state)
        else:
            button = get_button("BLOCK", self.state)
        self.blocks.extend([get_text_section(text), button])
        res = requests.post(
            url=self.response_url,
            headers=self.headers,
            json={
                "channel": self.channel,
                "blocks": self.blocks,
                "ts": self.msg_ts,
            },
        )
        print(f"send_locked: {res.json()}")

    def send_approved(self):
        self.blocks.append(APPROVED_SECTION)
        res = requests.post(
            url=self.response_url,
            headers=self.headers,
            json={
                "channel": self.channel,
                "blocks": self.blocks,
                "ts": self.msg_ts,
            },
        )
        print(f"send_approved: {res.json()}")

    def send_exception(self, exception):
        res = requests.post(
            url=WRITE_URL,
            headers=self.headers,
            json={
                "channel": self.channel,
                "text": f"{exception}",
                "thread_ts": self.msg_ts,
            },
        )
        print(f"send_exception: {res.json()}")

    # def send_thread_unlock(self):
    #     self.blocks.append(get_unlock_button(self.state))
    #     res = requests.post(
    #         url=WRITE_URL,
    #         headers=self.headers,
    #         json={
    #             "channel": self.channel,
    #             "blocks": self.blocks,
    #             "thread_ts": self.msg_ts,
    #         },
    #     )
    #     print(f"send_thread_unlock: {res.json()}")

    @property
    def state(self):
        return self.value

    @property
    def user(self):
        # {id, username, team_id}
        return self._user
