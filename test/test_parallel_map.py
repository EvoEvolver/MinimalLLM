from mllm.utils.maps import parallel_map, p_map
import time
def test_parallel_map():
    def wait_for_1_second(x):
        time.sleep(0.2)
        return x**2

    for i, res in parallel_map(wait_for_1_second, [1, 2, 3], n_workers=1, title="test"):
        print(res)
def test_p_map():
    def wait_for_1_second(x):
        time.sleep(0.2)
        return x**2

    for arg, res in p_map(wait_for_1_second, [1, 2, 3], n_workers=1, title="test"):
        print(arg, res)
        assert arg**2 == res
