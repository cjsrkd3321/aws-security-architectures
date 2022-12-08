from os import environ
from datetime import datetime
from resources.utils import has_value_from_tags

import time
import pytz

environ["TZ"] = "UTC"
utc = pytz.UTC
time.tzset()

now = utc.localize(datetime.now())

# identifies untagged resources
def have_tags(resource):
    if "tags" in resource and resource["tags"]:
        return True
    return False


def have_no_nuke_project_tag(resource):
    if "tags" not in resource:
        return False
    return not has_value_from_tags(resource.get("tags"), "Project", "nuke")


def is_create_date_less_than_now(resource):
    if "create_date" not in resource:
        return False
    cd = resource["create_date"]
    if type(cd) == int:
        cd = datetime.fromtimestamp(cd / 1_000)
    elif type(cd) == str:
        try:
            cd = datetime.fromtimestamp(int(cd))
        except ValueError:
            if cd.endswith("Z"):
                cd = datetime.strptime(cd, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                cd = datetime.strptime(cd, "%Y-%m-%d %H:%M:%S.%f")
    if not cd.tzinfo:
        cd = utc.localize(cd)
    cd = cd.replace(tzinfo=utc)

    return cd < now
