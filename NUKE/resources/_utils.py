def get_name_from_tags(tags):
    if not tags:
        return None
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None


# identifies untagged resources
def filter_func(resources):
    return [r for r in resources if not r["tags"]]
