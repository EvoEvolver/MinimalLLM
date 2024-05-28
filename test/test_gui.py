from mllm import caching, display_chats, Chat
from mllm.debug import display_embed_search
from mllm.embedding import get_vector_store_from_str


def test_image_display():
    with caching.refresh_cache():
        with display_chats():
            chat = Chat()
            chat.add_user_message("What is in this image?")
            chat.add_image_message(
                "EvoLogoOrg.png")
            res = chat.complete(cache=True)

def test_cached_display():
    with caching.refresh_cache():
        chat = Chat()
        chat.add_user_message("What is your name?")
        res1 = chat.complete(cache=True)
    with display_chats():
        chat = Chat()
        chat.add_user_message("What is your name?")
        res2 = chat.complete(cache=True)
        assert res1 == res2

def test_vector_store_display():
    with display_embed_search():
        vector_store = get_vector_store_from_str(["banana", "headset", "Mike"])
        res = vector_store.get_top_k_items(["earphone", "PC"])
        assert res[0] == "headset"