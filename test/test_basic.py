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
    chat += "Can you give more information about it?"
    res = chat.complete()
    print(chat)


def test_system_message():
    chat = Chat(system_message="You are an assistant who only reply in `yes` or `no`")
    chat += "Are you a human?"
    res = chat.complete()
    print(res)

def test_auto_dedent():
    prompt = """
    Explain the following code
    ```python
    print("Hello")
    greet()
    ```
    """
    prompt += "What is the output?"
    chat = Chat(prompt, dedent=True)
    message = chat.get_messages_to_api()
    assert message[0]["content"] == """
Explain the following code
```python
print("Hello")
greet()
```
What is the output?"""