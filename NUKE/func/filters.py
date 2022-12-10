from os import environ
from datetime import datetime
from resources.utils import has_value_from_tags
from resources.utils import convert_time_to_datetime

import time
import pytz

environ["TZ"] = "UTC"
utc = pytz.UTC
time.tzset()

now = utc.localize(datetime.now())

# Filter resources with tags if exist
def have_tags(resource):
    if "tags" in resource and resource["tags"]:
        return True
    return False


# Filter resources with no "Project=nuke" tag
def have_no_nuke_project_tag(resource):
    if "tags" not in resource:
        return False
    return not has_value_from_tags(resource.get("tags"), "Project", "nuke")


# Filter resources with create_date if exist and less than now
def is_create_date_less_than_now(resource):
    if "create_date" not in resource:
        return False
    cd = convert_time_to_datetime(resource["create_date"], utc)
    return cd < now
