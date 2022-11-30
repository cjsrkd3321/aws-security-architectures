from resources._utils import get_value_from_tags


# identifies untagged resources
def have_tags(resource):
    if "tags" in resource and resource["tags"]:
        return True
    return False


def have_no_nuke_project_tag(resource):
    return not get_value_from_tags(resource.get("tags"), "Project", "nuke")
