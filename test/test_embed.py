from mllm.embedding import get_vector_store_from_str


def test_vector_store_basic():
    vector_store = get_vector_store_from_str(["banana", "headset", "Mike"])
    res = vector_store.get_similarities_from_str("earphone")
    assert res[0] == "headset"
    res = vector_store.get_similarities_from_str("apple")
    assert res[0] == "banana"
    res = vector_store.get_similarities_from_str("Jackson")
    assert res[0] == "Mike"