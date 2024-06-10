from __future__ import annotations

import inspect
import os
import atexit
import sys

from mllm.cache.cache_embedding import CacheTableEmbed
from mllm.cache.cache_kv import CacheTableKV

def get_main_path():
    return os.path.abspath(sys.argv[0])


def get_cache_path(main_path: str):
    file_name = os.path.basename(main_path)
    dir_name = os.path.dirname(main_path)
    return os.path.join(dir_name, ".llm_cache", file_name + ".json")


class CacheService:

    def __init__(self, base_path=None):
        if base_path is None:
            cache_path = get_cache_path(get_main_path())
        else:
            cache_path = get_cache_path(base_path)
        self.cache_kv: CacheTableKV = CacheTableKV(cache_path)
        self.cache_embed: CacheTableEmbed = CacheTableEmbed(os.path.dirname(cache_path))
        self.cache_kv_other = {self.cache_kv.cache_path: self.cache_kv}
        self.cache_embed_other = {self.cache_kv.cache_path: self.cache_embed}

    def save(self):
        self.cache_kv.save_all_cache_to_file()
        self.cache_embed.save_cache_table()

    def save_used(self):
        n_remove = self.cache_kv.filter_unused_cache()
        if n_remove > 0:
            print(f"Removed {n_remove} unused cache")
        self.cache_kv.save_all_cache_to_file()
        # TODO: save only used embedding cache
        self.cache_embed.save_cache_table()

    def set_main_here(self):
        # get the file path of the caller use inspect
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        main_path = os.path.abspath(module.__file__)
        self._load_cache_on_path(main_path)

    def refresh_cache(self, disable=False):
        """
        Usage: with caching.refresh_cache():
                your codes
        :return: a context manager that refreshes the cache
        """
        return RefreshCacheContext(self.cache_kv, disable=disable)

    def disable_cache(self, disable=False):
        """
        Usage: with caching.disable_cache():
                your codes
        :return:
        """
        return DisableCacheContext(self.cache_kv, disable=disable)

    def _load_cache_on_path(self, main_path):
        cache_path = get_cache_path(main_path)
        cache_dir = os.path.dirname(cache_path)

        if cache_path in self.cache_kv_other:
            self.cache_kv = self.cache_kv_other[cache_path]
        else:
            self.cache_kv = CacheTableKV(cache_path)
            self.cache_kv_other[cache_path] = self.cache_kv

        if cache_dir in self.cache_embed_other:
            self.cache_embed = self.cache_embed_other[cache_dir]
        else:
            self.cache_embed = CacheTableEmbed(cache_dir)
            self.cache_embed_other[cache_dir] = self.cache_embed


class RefreshCacheContext:
    def __init__(self, cache_kv: CacheTableKV, cache_type: str = "", disable=False):
        """
        :param cache_type: The type of cache to refresh. If type is "", then all cache will be
        refreshed
        """
        self.cache_type = cache_type
        self.cache_kv = cache_kv
        self.already_refreshed = False
        self.disable = True if disable != False else False

    def __enter__(self):
        if self.disable:
            return
        if self.cache_type != "":
            if self.cache_type not in self.cache_kv.types_to_refresh:
                self.cache_kv.types_to_refresh.add(self.cache_type)
            else:
                self.already_refreshed = True
        else:
            if self.cache_kv.refresh_all:
                self.already_refreshed = True
            else:
                self.cache_kv.refresh_all = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.disable:
            return
        if self.cache_type != "":
            if not self.already_refreshed:
                self.cache_kv.types_to_refresh.remove(self.cache_type)
        else:
            if not self.already_refreshed:
                self.cache_kv.refresh_all = False
        self.cache_kv.apply_cache_update()


class DisableCacheContext:
    def __init__(self, cache_kv: CacheTableKV, disable=False):
        self.cache_kv: CacheTableKV = cache_kv
        self.disable = True if disable != False else False

    def __enter__(self):
        if self.disable:
            return
        self.cache_kv.inactive = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.disable:
            return
        self.cache_kv.inactive = False


caching = CacheService()

# save cache on exit
atexit.register(caching.save)
