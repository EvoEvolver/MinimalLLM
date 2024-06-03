from __future__ import annotations

import hashlib
from typing import List, Dict

import numpy as np
from litellm import embedding
from mllm.cache.cache_service import caching
from mllm.config import default_models


class LazyEmbedding:
    lazy_embeddings: Dict[str, List[LazyEmbedding]] = {}

    def __init__(self, src: str, model: str, hash_key, cache_table):
        self.src = src
        self.model = model
        self.hash_key = hash_key
        self.cache_table = cache_table
        self.embedding = None
        if model not in LazyEmbedding.lazy_embeddings:
            LazyEmbedding.lazy_embeddings[model] = [self]
        else:
            LazyEmbedding.lazy_embeddings[model].append(self)


    def __array__(self):
        if self.embedding is None:
            self.flush()
        return self.embedding

    def to_list(self):
        return list(self.__array__())

    def flush(self):
        lazy_embeddings = LazyEmbedding.lazy_embeddings[self.model]
        embeddings = _get_embeddings(self.model, [le.src for le in lazy_embeddings])
        for i, item in enumerate(lazy_embeddings):
            item.embedding = embeddings[i]
            self.cache_table[item.hash_key] = item.embedding
        LazyEmbedding.lazy_embeddings[self.model] = []

    def __str__(self):
        return str(self.__array__())

    def __repr__(self):
        return repr(self.__array__())


def get_embeddings(texts: list[str], model=None, lazy=True) -> list[list[float]]:
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
        if not lazy:
            res = _get_embeddings(model, texts_without_cache)
            for i, r in zip(index_for_eval, res):
                cache_table[hash_keys[i]] = r
                embeddings[i] = r
        else:
            for i in index_for_eval:
                le = LazyEmbedding(texts[i], model, hash_keys[i], cache_table)
                embeddings[i] = le

    return embeddings


def _get_embeddings(model, texts_without_cache):
    res = embedding(model, input=texts_without_cache)
    res = [np.array(r['embedding']) for r in res.data]
    return res
