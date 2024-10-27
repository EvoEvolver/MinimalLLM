from mllm.structured_chat import SChat


def test_basic_schat():
    chat = SChat()
    chat.add_block("background", "You generating a random number.")
    chat.add_output_key("number", "int", "The generated number.")
    res = chat.complete()
    print(res)