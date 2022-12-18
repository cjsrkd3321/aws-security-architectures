import hmac
import hashlib
import time


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
