import concurrent.futures
import time
from typing import List

from mllm.utils.ipython import is_in_notebook

if is_in_notebook:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


"""
# Parallel map
"""


default_parallel_map_config = {
    "n_workers": 8
}


def parallel_map(func, *args, n_workers=None, title=None):
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
    title = title or func.__name__
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
        results = []
        for result in tqdm(executor.map(func, *arg_lists, timeout=None), total=len(arg_lists[0]),
                           desc=title):
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
