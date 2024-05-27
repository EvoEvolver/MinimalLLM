from __future__ import annotations

import hashlib
from litellm import embedding
from mllm.cache.cache_service import caching
from mllm.config import default_models



def get_embeddings(texts: list[str], model=None) -> list[list[float]]:
    if model is None:
        model = default_models["embedding"]

    cache_table = caching.cache_embed.load_cache_table(model)
    hash_keys = [hashlib.md5(text.encode()).hexdigest() for text in texts]

    embeddings = []
    index_for_eval = []
    texts_without_cache = []
    for i, text in enumerate(texts):
        if len(text) == 0:
            embeddings.append(0)
            continue
        if hash_keys[i] not in cache_table:
            texts_without_cache.append(text)
            embeddings.append(None)
            index_for_eval.append(i)
        else:
            embeddings.append(cache_table[hash_keys[i]])
    if len(texts_without_cache) > 0:
        try:
            res = embedding(model, input=texts_without_cache)
        except Exception as e:
            print(e)
            print(texts_without_cache)
            raise e
        res = [r['embedding'] for r in res.data]
        for i, r in zip(index_for_eval, res):
            cache_table[hash_keys[i]] = r
            embeddings[i] = r

    return embeddings
