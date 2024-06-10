import mllm
from mllm import Chat
from mllm.embedding import get_vector_store_from_str


def test_image_display():
    with mllm.debug.display_chats():
        chat = Chat()
        chat.add_user_message("What is in this image?")
        chat.add_image_message(
            "EvoLogoOrg.png")
        res = chat.complete(cache=True)

def test_chat_with_html_tags():
    with mllm.debug.display_chats():
        chat = Chat()
        chat.add_user_message("<input>What is your name?</input>")
        res1 = chat.complete()


def test_cached_display():
    with mllm.debug.refresh_cache():
        chat = Chat()
        chat.add_user_message("What is your name?")
        res1 = chat.complete(cache=True)
    with mllm.debug.display_chats():
        chat = Chat()
        chat.add_user_message("What is your name?")
        res2 = chat.complete(cache=True)
        assert res1 == res2

def test_chat_display_with_indent():
    with mllm.debug.display_chats():
        chat = Chat()
        chat.add_user_message("""
Explain the following code
```python
def greet():
    print("Hello")
greet()
```
""")
        res = chat.complete(cache=True)


def test_vector_store_display():
    with mllm.debug.display_embed_search():
        vector_store = get_vector_store_from_str(["banana", "headset", "Mike"])
        res = vector_store.get_top_k_items(["earphone", "PC"])
        assert res[0] == "headset"

