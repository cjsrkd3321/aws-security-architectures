from functools import wraps
import time


def get_name_from_tags(tags):
    if not tags:
        return None
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None


def get_value_from_tags(tags, key, value):
    if not tags:
        return False
    for tag in tags:
        if tag.get("Key") == key:
            return tag.get("Value") == value
    return False


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
