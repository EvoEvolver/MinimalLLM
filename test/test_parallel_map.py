from mllm.utils.maps import parallel_map
import time
def test_parallel_map():
    def wait_for_1_second(x):
        time.sleep(1)
        return x

    for i, res in parallel_map(wait_for_1_second, [1, 2, 3], n_workers=1, title="test"):
        print(res)
