from mllm.utils import debugger_is_active

is_debug = debugger_is_active()

def display_chats(disable=False):
    from mllm.chat import ChatLogger
    return ChatLogger(disable)


def display_embed_search(disable=False):
    from mllm.embedding.vector_store import EmbedSearchLogger
    return EmbedSearchLogger(disable)