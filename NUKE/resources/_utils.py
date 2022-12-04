from functools import wraps
import time


def get_name_from_tags(tags):
    if not tags:
        return None
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None


def has_value_from_tags(tags, key, value):
    if not tags:
        return False
    for tag in tags:
        if tag.get("Key") == key:
            return tag.get("Value") == value
    return False


def delete_tag_prefix(tags):
    new_tags = []
    if not tags:
        return new_tags
    for tag in tags:
        key, value = tag.items()
        new_tags.append({"Key": key[1], "Value": value[1]})
    return new_tags


def convert_dict_to_tags(tags):
    new_tags = []
    if not tags:
        return new_tags
    for key, value in tags.items():
        new_tags.append({"Key": key, "Value": value})
    return new_tags


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper
