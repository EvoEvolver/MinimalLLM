import os

from mllm import Chat


def test_no_api_key():
    os.environ["OPENAI_API_KEY"] = ""
    chat = Chat()
    chat.add_user_message("What is your name?")
    res = chat.complete()

def test_failed_parsing():
    chat = Chat()
    chat.add_user_message("What is your name?")
    res = chat.complete(parse="dict")