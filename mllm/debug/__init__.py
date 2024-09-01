from mllm.cache.cache_service import caching

def display_chats(disable=False):
    from mllm.chat_logger import ChatLogger
    return ChatLogger(disable)

def log_chats(disable=False, show_table=True, save_path=None):
    from mllm.chat_logger import ChatLogger
    return ChatLogger(disable, save_path=save_path, show_table=show_table)

def display_embed_search(disable=False):
    from mllm.embedding.vector_store import EmbedSearchLogger
    return EmbedSearchLogger(disable)


def refresh_cache(disable=False):
    return caching.refresh_cache(disable)