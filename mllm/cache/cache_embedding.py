import hashlib
import os

import numpy as np
import sqlite3
from datetime import date

from mllm.cache.conn_pool import ConnPool


def get_hash(text: str):
    return hashlib.md5(text.encode()).hexdigest()

class CacheTableEmbed:
    def __init__(self, cache_dir: str, post_fix=""):
        self.cache_dir = cache_dir
        self.post_fix = post_fix
        self.pending_cache = {}
        db_path = self.get_db_path()
        db_exist = os.path.exists(db_path)
        self.conn_pool = ConnPool(self.get_db_path())
        if not db_exist:
            self.create_cache_table()

    @property
    def db_conn(self):
        return self.conn_pool.get_conn()

    def create_cache_table(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE embedding_cache
                         (hash TEXT PRIMARY KEY, 
                         model_name text, 
                         date text,
                         embedding blob)''')
        self.db_conn.commit()

    def add_cache(self, model_name: str, text: str, embedding: np.ndarray):
        hash_value = get_hash(text)
        self.pending_cache[(model_name, hash_value)] = embedding

    def read_cache(self, model_name: str, text: str) -> np.ndarray:
        text_hash = get_hash(text)
        if (model_name, text_hash) in self.pending_cache:
            return self.pending_cache[(model_name, text_hash)]
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT embedding FROM embedding_cache WHERE hash = ? AND model_name = ?", (text_hash, model_name))
        res = cursor.fetchone()
        if res is None:
            return None
        return np.frombuffer(res[0], dtype=np.float32)

    def get_db_path(self):
        return os.path.join(self.cache_dir, f"embedding_cache{self.post_fix}.db")

    def save_pending_cache(self):
        for (model_name, hash_value), embedding in self.pending_cache.items():
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO embedding_cache VALUES (?, ?, ?, ?)", (hash_value, model_name, str(date.today()), embedding.tobytes()))
        self.db_conn.commit()

    def clear_cache_table(self):
        self.pending_cache = {}
        self.db_conn.execute("DELETE FROM embedding_cache")
        self.db_conn.commit()

    def close(self):
        self.conn_pool.close_all()
