import gzip
import json
import logging

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def jsonb_gzip_to_jsons(jsonb_gzip):
    jsonb = gzip.decompress(jsonb_gzip).decode()
    return [json.loads(jsonb) for jsonb in jsonb.split("\n") if jsonb]


def stream_to_str(body):
    return body.read().decode()


def convert_center_string_to_asterisk(data):
    data_size = len(data)
    boundary_index = data_size // 3
    if boundary_index != 0:
        return data[:boundary_index + 1] + "*" * boundary_index + data[boundary_index * 2 + 1:]
    else:
        return data


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


def get_slack_message(slack_channel, message, is_succeeded=True):
    return (
        {
            "channel": slack_channel,
            "attachments": [
                {
                    "color": "#30db3f" if is_succeeded else "#eb4034",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": message,
                            },
                        },
                    ],
                }
            ],
        },
    )[0]
