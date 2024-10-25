from mllm import caching
from mllm.chat import Chat
from mllm.utils import p_map

def test_cached_chat():
    def get_random_response():
        chat = Chat()
        chat += "Introduce your self in one sentence."
        res = chat.complete(cache=True, options={"temperature": 1})
        return res
    num_1 = get_random_response()
    num_2 = get_random_response()
    assert num_1 == num_2

## See all test_image_chat_cache in test_image.py

def test_multi_thread_cache():
    print(caching._cache_kv.cache_path)
    def get_the_same_number(num):
        chat = Chat(f"Output the number {num}")
        res = chat.complete(cache=True)
        return res

    res = p_map(get_the_same_number, range(10))
    caching.close()