import os

import numpy as np


class CacheTableEmbed:
    def __init__(self, cache_dir: str):
        self.cache_tables = {}
        self.cache_dir = cache_dir

    def load_cache_table(self, model_name: str):
        if model_name in self.cache_tables:
            return self.cache_tables[model_name]
        embedding_cache_path = get_cache_path(self.cache_dir, model_name)
        if os.path.exists(embedding_cache_path):
            embedding_cache = np.load(embedding_cache_path, allow_pickle=True).item()
        else:
            embedding_cache = {}
        self.cache_tables[model_name] = embedding_cache
        return embedding_cache

    def save_cache_table(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        for model_name in self.cache_tables:
            embedding_cache_path = get_cache_path(self.cache_dir, model_name)
            np.save(embedding_cache_path, self.cache_tables[model_name])


def get_cache_path(cache_dir, model_name):
    return os.path.join(cache_dir, f"embed_{model_name}.npy")
