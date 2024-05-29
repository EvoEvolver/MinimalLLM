

# Parsing rules for chats

## General usage

Passing `parse` argument to `Chat.complete` method, you can parse the result in a specific way.  
```python
from mllm import Chat
chat = Chat()
chat += "Output a JSON dict with keys 'a' and 'b' and values 1 and 2"
res = chat.complete(parse="dict")
print(res['a'])
```
Advantages of using the built-in parsing rules:

- Automated retry when the parsing fails
- Robust parsing rules that can handle various outputs.

## `dict`

Parse the result as a JSON dictionary using `json.loads`. This rule will ignore the `'''json` surrounding the output.

## `list`

Similar to `dict`, but parse the result as a python list. The parser will find the first `[` and the last `]` in the output and try to parse the content in between.

## `obj`

Similar to `dict`, but parse using `ast.literal_eval`. This rule is useful when the output is a python object.


## `quotes`

Parse the result as a string. This rule will ignore the ```xxx surrounding the output.
This rule is useful when you want the LLM to output codes.

```python
from mllm import Chat
chat = Chat()
chat += "Output a python code for quicksort. Start your answer with ```python"
res = chat.complete(parse="quotes")
print(res)
```


## `colon`

Capture the contents after the first colon `:` in the output. This rule is useful when you want to limit the topic of the output.

```python
from mllm import Chat
chat = Chat()
chat += "Summarize the following text:<text> This is a test.</text>"
chat += "Start your answer with Summary:"
res = chat.complete(parse="colon")
print(res)
```