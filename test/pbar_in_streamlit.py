from time import sleep
from stqdm import stqdm
from mllm.utils import p_map

wait_for_1_second = lambda x: sleep(1) or x**2
p_map(wait_for_1_second, [1, 2, 3], n_workers=1, title="test", pbar_impl=stqdm)