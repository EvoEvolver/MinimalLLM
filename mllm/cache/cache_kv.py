from __future__ import annotations

import hashlib
import json
import os
from datetime import date
from typing import Dict, Optional, Set

from mllm.cache.conn_pool import ConnPool


def get_hash(data: any) -> str:
    return hashlib.sha1(json.dumps(data).encode("utf-8")).hexdigest()


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
        self.meta = meta or {}

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


class CacheTableKV:
    def __init__(self, cache_path: str):
        self.cache_path = cache_path
        # List of pending cache
        self.pending_cache: Dict[str, Cache] = {}
        # List of active cache. Used for garbage collection
        self.active_cache_hash: Set[str] = set()
        #
        self.types_to_refresh: Set[str] = set()
        #
        self.refresh_all: bool = False
        #
        self.inactive = False

        db_path = cache_path
        db_exist = os.path.exists(db_path)
        db_dir = os.path.dirname(db_path)
        # create the directory if not exist
        if len(db_dir) != 0:
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
        self.conn_pool = ConnPool(db_path)
        if not db_exist:
            self.create_cache_table()

    def create_cache_table(self):
        db_conn = self.conn_pool.get_conn()
        cursor = db_conn.cursor()
        cursor.execute('''CREATE TABLE cache_table
                         (hash TEXT PRIMARY KEY,
                         type text,
                         value text,
                         date text,
                         meta text)''')
        db_conn.commit()

    def save_all_cache_to_file(self, filter_unused_cache=False):
        if filter_unused_cache:
            n_remove = self.filter_unused_cache()
            if n_remove > 0:
                print(f"Removed {n_remove} unused cache")
        self.apply_cache_update()

    def filter_unused_cache(self) -> int:
        # remove all the rows whose hash is not in self.active_cache_hash
        db_conn = self.conn_pool.get_conn()
        cursor = db_conn.cursor()
        n_rows = cursor.execute("SELECT COUNT(*) FROM cache_table").fetchone()[0]
        cursor.execute("DELETE FROM cache_table WHERE hash NOT IN ({})".format(
            ",".join(["?"] * len(self.active_cache_hash))), tuple(self.active_cache_hash))
        n_rows_after = cursor.execute("SELECT COUNT(*) FROM cache_table").fetchone()[0]
        db_conn.commit()
        return n_rows - n_rows_after

    def read_cache(self, input: any, type: str, create_cache=True) -> Cache | None:

        if self.inactive:
            return None
        hash = get_hash(input)

        db_conn = self.conn_pool.get_conn()
        cursor = db_conn.cursor()
        cursor.execute("SELECT value, meta FROM cache_table WHERE hash = ? AND type = ?", (hash, type))
        db_conn.commit()
        res = cursor.fetchone()

        meta = {}
        cache_value = None
        if res is None:
            un_hit = True
        else:
            cache_value, meta = res
            if meta != "None":
                meta = json.loads(meta)
            else:
                meta = {}
            un_hit = False

        if type in self.types_to_refresh or self.refresh_all:
            un_hit = True
        if un_hit:
            if create_cache:
                new_cache = Cache(None, hash, input, type, meta)
                self.add_cache(new_cache)
                return new_cache
            else:
                return None

        cache_hit = Cache(cache_value, hash, input, type, meta)
        self.active_cache_hash.add(hash)

        return cache_hit

    def add_cache(self, cache: Cache):
        self.pending_cache[cache.hash] = cache

    def apply_cache_update(self):
        remaining_cache = {}
        db_conn = self.conn_pool.get_conn()
        cursor = db_conn.cursor()
        for hash, cache in list(self.pending_cache.items()):
            if cache.is_valid():
                self.active_cache_hash.add(cache.hash)
                cursor.execute("INSERT OR REPLACE INTO cache_table VALUES (?, ?, ?, ?, ?)",
                               (cache.hash, cache.type, cache.value, str(date.today()), str(cache.meta)))

            else:
                remaining_cache[hash] = cache
        db_conn.commit()
        self.pending_cache = remaining_cache

    def discard_cache_update(self):
        self.pending_cache = {}

    def close(self):
        self.conn_pool.close_all()




