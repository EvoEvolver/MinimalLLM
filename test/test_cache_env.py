
from mllm import caching

def test_env():
    with caching.refresh_cache():
        with caching.cache_env("t"):
            cache = caching.cache_kv.read_cache("123", "int")
            cache.set_cache("1234")

        cache = caching.cache_kv.read_cache("123", "int")
        cache.set_cache("12345")

        with caching.cache_env("t"):
            cache = caching.cache_kv.read_cache("123", "int")
            assert cache.value == "1234"