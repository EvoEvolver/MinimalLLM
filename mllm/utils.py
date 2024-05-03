import ast
import concurrent.futures
import json
import os
import sys
import time
from typing import List, Any

from tenacity import retry, stop_after_attempt, wait_fixed, \
    retry_if_exception, stop_after_delay
from tqdm import tqdm


class Parse:

    @staticmethod
    def obj(src: str):
        try:
            res = ast.literal_eval(src)
        except:
            raise ValueError(f"Invalid Python code: {src}")
        return res

    @staticmethod
    def dict(src: str):
        # find first {
        start = src.find("{")
        # find last }
        end = src.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"Invalid json: {src}")
        try:
            # res = ast.literal_eval(src[start:end + 1])
            res = json.loads(src[start:end + 1])
        except:
            raise ValueError(f"Invalid json: {src}")
        return res

    @staticmethod
    def list(src):
        # find first [
        start = src.find("[")
        # find last ]
        end = src.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"Invalid json: {src}")
        try:
            res = json.loads(src[start:end + 1])
        except:
            raise ValueError(f"Invalid json: {src}")
        return res

    @staticmethod
    def quotes(src: str):
        """
        Parse a string that is enclosed by quotes ```
        :param src:
        :return: contents of the quoted string
        """
        split_lines = src.split("\n")
        for start, line in enumerate(split_lines):
            if line.startswith("```"):
                title = line[3:]
                break
        else:
            raise ValueError("No closing quotes")
        for end in range(start+1, len(split_lines)):
            if split_lines[end].startswith("```"):
                break
        else:
            raise ValueError("No closing quotes")
        contents = "\n".join(split_lines[start + 1: end])
        return contents

    @staticmethod
    def colon(src: str):
        """
        Parse a string that is separated by colons
        :param src:
        :return: the contents after the colon
        """
        split = src.split(":")
        if len(split) != 2:
            raise ValueError("Invalid colon string")
        contents = split[1].strip()
        return contents


"""
# Parallel map
"""

default_parallel_map_config = {
    "n_workers": 8
}

def parallel_map(func, *args, n_workers=None):
    """
    Example usage: `for i, res in parallel_map(lambda x: x + 1, [1, 2, 3, 4, 5], n_workers=4): do_something`
    :param func: The function to apply on each element of args
    :param args: The arguments to apply func
    :param n_workers: Number of workers
    :return:
    """
    # Use concurrent.futures.ThreadPoolExecutor to parallelize
    # Use tqdm to show progress bar
    from mllm.cache.cache_service import caching
    if n_workers is None:
        n_workers = default_parallel_map_config["n_workers"]

    arg_lists = [list(arg) for arg in args]
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
        results = []
        for result in tqdm(executor.map(func, *arg_lists, timeout=None), total=len(arg_lists[0]),
                           desc=func.__name__):
            results.append(result)
            time_now = time.time()
            if time_now - start_time > 5:
                caching.save()
                start_time = time_now
    caching.save()
    return enumerate(results)


"""
# Nested map
"""


def nested_map(func, nested_list: List):
    """
    Apply func to each element in nested_list and return a nested list with the same structure
    Precondition: list nested can only contain either list or non-list
    :param func:
    :param nested_list:
    :return:
    """
    flat_list = []
    add_to_flat_list(flat_list, nested_list)
    flat_res = func(flat_list)
    nested_res = make_nested_list(flat_res, nested_list)
    return nested_res


def add_to_flat_list(flat_list, nested_list):
    if isinstance(nested_list[0], list):
        for nested_list_ in nested_list:
            add_to_flat_list(flat_list, nested_list_)
    else:
        flat_list.extend(nested_list)


def make_nested_list(flattened_res, nested_list):
    if not isinstance(nested_list[0], list):
        return flattened_res
    nested_res = []
    i = 0
    for nested_list_ in nested_list:
        nested_res.append(
            make_nested_list(flattened_res[i: i + len(nested_list_)], nested_list_))
        i += len(nested_list_)
    return nested_res


def test_nested_map():
    before_map = [[[1], [2]], [3, 4, 5]]
    after_map = nested_map(lambda arr: list(map(lambda x: x + 1, arr)), before_map)
    assert after_map == [[[2], [3]], [4, 5, 6]]


"""
# Debug and retry decorator
"""


def debugger_is_active() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None


def get_main_path():
    return os.path.abspath(sys.argv[0])


standard_multi_attempts = retry(
    wait=wait_fixed(0.5),
    stop=(stop_after_attempt(3)),
    retry=retry_if_exception(lambda e: True),
    reraise=False,
)


def test_standard_multi_attempts():
    @standard_multi_attempts
    def a():
        print("a")
        raise ValueError("a")

    a()

class EmptyContext:
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass