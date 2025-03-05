from mllm import Chat
from mllm.provider_switch import set_default_to_deepseek
from mllm.utils.parser import Parse, parse_json_by_cheap_model


def test_parse_quotes():
    src = """
123
```python
This is a quoted string
```
123
"""
    res = Parse.quotes(src)
    assert res == "This is a quoted string"

def test_parse_quotes3():
    src = """
123
123
"""
    res = Parse.quotes(src)
    print(res)
    assert res == "This is a quoted string"

def test_parse_colon():
    src = "title: This is a colon string"
    res = Parse.colon(src)
    assert res == "This is a colon string"

def test_code_gen():
    prompt = """
Generate a code for bubble sort.
Start your answer with ```python
"""
    chat = Chat()
    chat += prompt
    res = chat.complete(parse="quotes")
    print(res)

def test_dict_gen():
    prompt = """
Generate a json dict with keys 'a' and 'b' and values 1 and 2
"""
    chat = Chat()
    chat += prompt
    res = chat.complete(parse="dict", cache=False)
    assert res == {"a": 1, "b": 2}


def test_model_correct():
    raw_json = """
{
no_quote : "
string 
with 
line 
change
"
}    
   
"""
    res = parse_json_by_cheap_model(raw_json)
    assert res == {'no_quote': '\nstring \nwith \nline \nchange\n'}