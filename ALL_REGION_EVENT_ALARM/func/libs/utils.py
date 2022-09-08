import json
import logging

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def send_message_to_slack(hook_url, slack_message, logger=logging.getLogger()):
    req = Request(hook_url, json.dumps(slack_message).encode("utf-8"))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message["channel"])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)