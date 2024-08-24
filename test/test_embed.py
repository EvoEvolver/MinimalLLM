from mllm import get_embeddings, caching
from mllm.config import default_models
from mllm.embedding import get_vector_store_from_str


def test_vector_store_basic():
    vector_store = get_vector_store_from_str(["banana", "headset", "Mike"])
    res = vector_store.get_top_k_items("earphone")
    assert res[0] == "headset"
    res = vector_store.get_top_k_items("apple")
    assert res[0] == "banana"
    res = vector_store.get_top_k_items("Jackson")
    assert res[0] == "Mike"

def test_vector_store_basic2():
    vector_store = get_vector_store_from_str(["banana", "headset", "Mike"])
    res = vector_store.get_top_k_items(["earphone", "PC"])
    assert res[0] == "headset"

def test_lazy_embedding():
    get_embeddings("1")
    caching.cache_embed.clear_cache_table()

    texts_1 = ["banana", "headset", "Mike"]
    texts_2 = ["earphone", "PC"]

    res_1 = get_embeddings(texts_1)
    res_2 = get_embeddings(texts_2)

    print(res_1)
    print(res_2)