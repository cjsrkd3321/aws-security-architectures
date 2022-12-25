import base64
import json

from req import Req


def lambda_handler(event, _):
    print(event)

    if "pathParameters" not in event:
        return {
            "statusCode": 400,
            "body": json.dumps("DOMAIN/[PATH] please"),
        }

    host = event["pathParameters"]["proxy"]
    headers = event["headers"]
    method = event["requestContext"]["http"]["method"]
    params = event.get("queryStringParameters", {})  # GET
    body = (
        str(base64.b64decode(event.get("body")), "utf-8")
        if event.get("isBase64Encoded")
        else event.get("body")
    )  # POST, PUT, PATCH

    if "amazonaws.com" in host:
        # https://docs.aws.amazon.com/ko_kr/general/latest/gr/sigv4-signed-request-examples.html
        url = f"https://{host}/{host}"
    else:
        url = f"https://{host}"
        headers["host"] = host.split("/")[0]

    r = Req(method, url, headers)
    res = r.request(params, data=body)
    return res
