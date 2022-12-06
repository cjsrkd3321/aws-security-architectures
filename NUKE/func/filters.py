from resources._utils import has_value_from_tags


# identifies untagged resources
def have_tags(resource):
    if "tags" in resource and resource["tags"]:
        return True
    return False


def have_no_nuke_project_tag(resource):
    if "tags" not in resource:
        return False
    return not has_value_from_tags(resource.get("tags"), "Project", "nuke")
