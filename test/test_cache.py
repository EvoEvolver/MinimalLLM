from mllm.chat import Chat


def test_cached_chat():
    def get_random_number():
        chat = Chat()
        chat += "Give me a random number from 1 to 10"
        res = chat.complete(cache=True)
        return res
    num_1 = get_random_number()
    num_2 = get_random_number()
    assert num_1 == num_2

## See all test_image_chat_cache in test_image.py