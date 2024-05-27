from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, Optional, List, Set



def get_hash(data: any, type: str) -> str:
    return hashlib.sha1(json.dumps([data, type]).encode("utf-8")).hexdigest()


class Cache:
    """
    The class for storing cache.
    """

    def __init__(self, value, hash: str, input: any, type: str,
                 meta: Optional[Dict] = None):
        self.value = value
        # self.hash should be the same as get_hash(input, type)
        self.hash: str = hash
        self.input: any = ""#input
        self.type: str = type
        self.meta = meta

    def get_self_dict(self):
        return {
            "value": self.value,
            "hash": self.hash,
            "input": self.input,
            "type": self.type,
            "meta": self.meta
        }

    def set_cache(self, value: any, meta: Optional[Dict] = None):
        self.value = value
        self.meta = meta

    def is_valid(self):
        return self.value is not None


CacheTable = Dict[str, Cache]


def serialize_cache_table(cache_table: Dict[str, Cache]):
    res = []
    for key, cache in cache_table.items():
        res.append(cache.get_self_dict())
    return json.dumps(res, indent=1)


class CacheTableKV:
    def __init__(self, cache_path: str):
        self.cache_path = cache_path
        # Map from hash to cache
        self.cache_table: Dict[str, Cache] = self.load_cache_table()
        # List of pending cache
        self.pending_cache: List[Cache] = []
        # List of active cache. Used for garbage collection
        self.active_cache_hash: Set[str] = set()
        #
        self.types_to_refresh: Set[str] = set()
        #
        self.refresh_all: bool = False
        #
        self.types_used: Set[str] = set()
        #
        self.inactive = False

    def save_all_cache_to_file(self):
        self.apply_cache_update()
        if len(self.cache_table) == 0:
            return
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w") as f:
            f.write(serialize_cache_table(self.cache_table))

    def filter_unused_cache(self) -> int:
        n_removed_cache = 0
        new_cache_table = {}
        for hash, cache in self.cache_table.items():
            if hash in self.active_cache_hash:
                new_cache_table[hash] = cache
            else:
                n_removed_cache += 1
        self.cache_table = new_cache_table
        return n_removed_cache

    def read_cache(self, input: any, type: str, create_cache=True) -> Cache | None:
        if self.inactive:
            return None
        hash = get_hash(input, type)
        self.types_used.add(type)
        un_hit = hash not in self.cache_table
        if type in self.types_to_refresh or self.refresh_all:
            un_hit = True
        if un_hit:
            if create_cache:
                new_cache = Cache(None, hash, input, type)
                self.add_cache(new_cache)
                return new_cache
            else:
                return None
        cache_hit = self.cache_table[hash]
        self.active_cache_hash.add(hash)
        return cache_hit

    def add_cache(self, cache: Cache):
        self.pending_cache.append(cache)

    def apply_cache_update(self):
        remaining_cache = []
        for cache in self.pending_cache:
            if cache.is_valid():
                self.active_cache_hash.add(cache.hash)
                self.cache_table[cache.hash] = cache
            else:
                remaining_cache.append(cache)
        self.pending_cache = remaining_cache

    def discard_cache_update(self):
        self.pending_cache = []

    def load_cache_table(self) -> CacheTable:
        if not os.path.exists(self.cache_path):
            return {}
        with open(self.cache_path, "r") as f:
            try:
                cache_list = json.load(f)
            except json.decoder.JSONDecodeError:
                cache_list = []
        cache_table = {}
        for cache_dict in cache_list:
            cache = Cache(cache_dict["value"], cache_dict["hash"], cache_dict["input"],
                          cache_dict["type"], cache_dict["meta"])
            cache_table[cache.hash] = cache
        return cache_table



