import requests


def delete_default_headers(headers):
    for key in (
        "x-forwarded-port",
        "x-forwarded-for",
        "x-forwarded-proto",
        "user-agent",
        "x-amzn-trace-id",
    ):
        headers.pop(key, None)
    return headers


class Req:
    def __init__(self, method, url, headers, timeout=5):
        self.method = method
        self.url = url
        self.headers = delete_default_headers(headers)
        self.timeout = timeout

    def request(self, params=None, data=None):
        r = requests.request(
            method=self.method,
            url=self.url,
            params=params,
            data=data,
            headers=self.headers,
            timeout=self.timeout,
        )
        return {
            "statusCode": r.status_code,
            "body": r.text,
            "headers": dict(r.headers),  # CaseInsensitiveDict to dict
        }
