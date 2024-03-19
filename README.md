# MinimalLLM

Minimal and handy interfaces of LLMs based on LiteLLM.

Features:
- Minimal and intuitive interfaces. You don't need to learn
- Handy cache system for faster testing
- Support for multiple LLMs by LiteLLM

## Usage

Chat
```python
from mllm import Chat
chat = Chat()
chat += "Give me a random number from 1 to 10"
res = chat.complete(cache=True)
print(res)
# Chats are cached if you like
```

Embedding
```python
from mllm import get_embeddings
embeddings = get_embeddings(["Hello, world!", "Goodbye, world!"])
print(embeddings)
# Embeddings are automatically cached
```

Switch provider
```python
from mllm.provider_switch import set_default_to_anthropic
set_default_to_anthropic()
```

Visualized Log of chats
```python
from mllm import Chat, display_chats
with display_chats():
    chat = Chat()
    chat += "Who is your developer?"
    res = chat.complete(cache=True)
    # A web page will be opened to show the chat log
```

## Installation

```bash
pip install -U git+https://github.com/EvoEvolver/MinimalLLM
```

To add it to your `requirements.txt`:
```
MinimalLLM @ git+https://github.com/EvoEvolver/MinimalLLM
```

## Why minimal?

Minimal means stable. We only provide the most basic interfaces and features.