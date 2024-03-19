from mllm.utils import debugger_is_active, EmptyContext

is_debug = debugger_is_active()

def display_chats(disable=None):
    if disable is not None:
        return EmptyContext()
    from mllm.chat import ChatLogger
    return ChatLogger()
