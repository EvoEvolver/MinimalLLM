from mllm.cache.cache_service import caching
from mllm.chat import Chat


def test_cached_chat():
    @auto_cache
    def get_random_number():
        chat = Chat()
        chat += "Give me a random number from 1 to 10"
        res = chat.complete()
        return res
    num_1 = get_random_number()
    print(num_1)
    caching.save()