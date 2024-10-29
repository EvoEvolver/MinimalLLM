from typing import Dict

from mllm import Chat
from mllm.chat import remove_all_indents


class JsonSpec:
    def __init__(self):
        self.keys = []

    def add_output_key(self, key: str, type: str, requirement: str = ""):
        requirement = remove_all_indents(requirement)
        requirement = requirement.strip()
        self.keys.append(
            {
                "key": key,
                "type": type,
                "requirement": requirement
            }
        )

    def in_prompt(self):
        keys = []
        for key_item in self.keys:
            key = key_item["key"]
            type = key_item["type"]
            requirement = key_item["requirement"]
            if len(requirement) > 0:
                keys.append(f'"{key}"({type}): {requirement}')
            else:
                keys.append(f'"{key}"({type})')
        keys = "\n".join(keys)
        prompt = f"<output>\nYou are required to output a JSON dict with the following keys:\n{keys}\n</output>"
        return prompt


class Block:
    def __init__(self, tagname: str, text: str):
        self.tagname = tagname
        self.text = text

    def in_prompt(self):
        return f"<{self.tagname}>\n{self.text}\n</{self.tagname}>"


class SChat:
    """
    The class for structured chat.
    """

    def __init__(self):
        self.blocks = []
        self.output_requirement = JsonSpec()

    def add_block(self, tagname: str, text: str, dedent=True):
        if dedent:
            text = remove_all_indents(text.strip())
        self.blocks.append(Block(tagname, text))

    def add_output_key(self, key: str, type: str, document: str):
        self.output_requirement.add_output_key(key, type, document)

    def in_prompt(self):
        res = []
        for block in self.blocks:
            res.append(block.in_prompt())
        res.append(self.output_requirement.in_prompt())
        res_str = "\n".join(res)
        return res_str

    def get_chat(self):
        chat = Chat()
        for block in self.blocks:
            chat += block.in_prompt()
        chat += self.output_requirement.in_prompt()
        return chat

    def complete(self, model=None, cache=False, expensive=False, options=None) -> Dict:
        res = self.get_chat().complete(model=model, cache=cache, expensive=expensive,
                                       parse="dict", retry=True, options=options)
        return res
