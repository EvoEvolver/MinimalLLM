from mllm import Chat


def test_image_chat():
    chat = Chat()
    chat.add_user_message("What is in this image?")
    chat.add_image_message(
        "EvoLogoOrg.png")
    res = chat.complete()
    print(res)