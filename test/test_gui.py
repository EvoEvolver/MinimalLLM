from mllm import caching, display_chats, Chat


def test_image_display():
    with caching.refresh_cache():
        with display_chats():
            chat = Chat()
            chat.add_user_message("What is in this image?")
            chat.add_image_message(
                "EvoLogoOrg.png")
            res = chat.complete(cache=True)