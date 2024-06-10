from mllm.cache.cache_service import caching

def display_chats(disable=False):
    from mllm.chat import ChatLogger
    return ChatLogger(disable)


def display_embed_search(disable=False):
    from mllm.embedding.vector_store import EmbedSearchLogger
    return EmbedSearchLogger(disable)


def refresh_cache(disable=False):
    return caching.refresh_cache(disable)