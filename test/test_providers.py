from mllm import Chat
from mllm.provider_switch import set_default_to_llama, set_default_to_anthropic, \
    set_default_to_gemini, set_default_to_deepseek


def test_deepseek():
    set_default_to_deepseek()
    run_chat()


def test_gemini():
    set_default_to_gemini()
    run_chat()

def test_image_gemini():
    set_default_to_gemini()
    run_image_chat()

def test_anthropic():
    set_default_to_anthropic()
    run_chat()

def test_image_anthropic():
    set_default_to_anthropic()
    run_image_chat()

def test_llama():
    set_default_to_llama()
    run_chat()

def test_image_llava():
    set_default_to_llama()
    run_image_chat()

def run_chat():
    chat = Chat(system_message="You are an assistant who only output JSON")
    chat += "What is your name"
    res = chat.complete(parse="dict")
    print(res)
    chat += "What is your birthdate"
    res = chat.complete(parse="dict")
    print(res)

def run_image_chat():
    chat = Chat(system_message="You are an assistant")
    chat += "What is in this image?"
    chat.add_image_message("EvoLogoOrg.png")
    res = chat.complete(cache=False)
    print(res)