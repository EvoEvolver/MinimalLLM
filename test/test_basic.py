from mllm.chat import Chat
from mllm.embedding import get_embeddings


def test_basic():
    inputs = ["a", "b", "c"]
    res = get_embeddings(inputs)
    print(res)


def test_chat():
    chat = Chat()
    chat.add_user_message("Who is your developer?")
    res = chat.complete()
    print(res)


def test_chat_plus():
    chat = Chat()
    chat += "Who is your developer?"
    res = chat.complete()
    print(res)


def test_system_message():
    chat = Chat(system_message="You are an assistant who only reply in `yes` or `no`")
    chat += "Are you a human?"
    res = chat.complete()
    print(res)