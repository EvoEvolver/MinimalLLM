# MinimalLLM

```bash
pip install MinimalLLM
```

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
chat = Chat()
chat += "Give a json dict with keys 'a' and 'b' and values 1 and 2"
res = chat.complete(parse="dict", cache=True)
print(res)
```

Embedding
```python
from mllm import get_embeddings
embeddings = get_embeddings(["Hello, world!", "Goodbye, world!"])
print(embeddings)
# Embeddings are automatically cached
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


## Providers

MinimalLLM is based on LiteLLM, which supports multiple providers. You can switch the provider to use different LLMs.

Switch provider
```python
from mllm.provider_switch import set_default_to_anthropic
set_default_to_anthropic()
```

To setup the API keys for the providers, we recommend to use the following streamlit app (run `pip install streamlit` first):
```python
from mllm.setup import run_setup_app
run_setup_app()
```

## Why minimal?

Minimal means stable. We only provide the most basic interfaces and features.
