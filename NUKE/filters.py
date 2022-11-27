# identifies untagged resources
def have_tags(resource):
    if "tags" in resource and resource["tags"]:
        return True
    return False
