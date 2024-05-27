from mllm.utils import debugger_is_active, EmptyContext

is_debug = debugger_is_active()

def display_chats(disable=None):
    if disable is not None:
        return EmptyContext()
    from mllm.chat import ChatLogger
    return ChatLogger()


def display_embed_search(disable=None):
    if disable is not None:
        return EmptyContext()
    from mllm.embedding.vector_store import EmbedSearchLogger
    return EmbedSearchLogger()