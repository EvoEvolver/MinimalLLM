from __future__ import annotations

from typing import List, Dict

import numpy as np
from litellm import embedding

from mllm.cache.cache_embedding import CacheTableEmbed
from mllm.cache.cache_service import caching
from mllm.config import default_models


class LazyEmbedding:
    lazy_embeddings: Dict[str, List[LazyEmbedding]] = {}

    def __init__(self, src: str, model: str, cache_embed: CacheTableEmbed):
        self.src = src
        self.model = model
        self.cache_embed: CacheTableEmbed = cache_embed
        self.embedding = None
        if model not in LazyEmbedding.lazy_embeddings:
            LazyEmbedding.lazy_embeddings[model] = [self]
        else:
            LazyEmbedding.lazy_embeddings[model].append(self)


    def __array__(self, *array_args, **array_kwargs):
        if self.embedding is None:
            self.flush()
        if len(array_args) > 0:
            return np.array(self.embedding, *array_args, **array_kwargs)
        return self.embedding

    def to_list(self):
        return list(self.__array__())

    def flush(self):
        lazy_embeddings = LazyEmbedding.lazy_embeddings[self.model]
        embeddings = _get_embeddings(self.model, [le.src for le in lazy_embeddings])
        for i, lazy_embedding in enumerate(lazy_embeddings):
            lazy_embedding.embedding = embeddings[i]
            self.cache_embed.add_cache(self.model, lazy_embedding.src, lazy_embedding.embedding)
        LazyEmbedding.lazy_embeddings[self.model] = []

    def __str__(self):
        return str(self.__array__())

    def __repr__(self):
        return repr(self.__array__())

    def __mul__(self, other):
        return self.__array__() * other


def get_embeddings(texts: list[str], model=None, lazy=True) -> list[list[float]]:
    if model is None:
        model = default_models["embedding"]
    cache_embed = caching.cache_embed

    embeddings = []
    index_for_eval = []
    texts_without_cache = []
    for i, text in enumerate(texts):
        if len(text) == 0:
            raise ValueError("Text cannot be empty")
            embeddings.append(0)
            continue
        embedding_from_cache = cache_embed.read_cache(model, text)
        if embedding_from_cache is None:
            texts_without_cache.append(text)
            embeddings.append(None)
            index_for_eval.append(i)
        else:
            embeddings.append(embedding_from_cache)
    if len(texts_without_cache) > 0:
        if not lazy:
            res = _get_embeddings(model, texts_without_cache)
            for i, r in zip(index_for_eval, res):
                cache_embed.add_cache(model, texts[i], r)
                embeddings[i] = r
        else:
            for i in index_for_eval:
                le = LazyEmbedding(texts[i], model, cache_embed)
                embeddings[i] = le

    return embeddings


def _get_embeddings(model, texts_without_cache):
    if len(texts_without_cache) > 2000:
        res = []
        for i in range(0, len(texts_without_cache), 2000):
            raw_res = embedding(model, input=texts_without_cache[i:i + 2000])
            res += [np.array(r['embedding'], dtype=np.float32) for r in raw_res.data]
        return res
    else:
        raw_res = embedding(model, input=texts_without_cache)
        res = [np.array(r['embedding'], dtype=np.float32) for r in raw_res.data]
        return res

