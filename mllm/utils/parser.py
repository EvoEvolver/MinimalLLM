import ast
import json
from dataclasses import dataclass

"""
# Parse
"""


@dataclass
class ParseOptions:
    cheap_model: str = "gpt-4o-mini"
    correct_json_by_model: bool = False


parse_options = ParseOptions()


class Parse:

    @staticmethod
    def obj(src: str):
        try:
            res = ast.literal_eval(src)
        except:
            raise ValueError(f"Invalid Python code: {src}")
        return res

    @staticmethod
    def dict(src: str):
        # find first {
        start = src.find("{")
        # find last }
        end = src.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"Invalid json: {src}")
        json_src = src[start:end + 1]

        try:
            res = json.loads(json_src)
            return res
        except:
            pass

        try:
            res = ast.literal_eval(json_src)
            return res
        except:
            pass

        json_src_replaced = json_src.replace("\n", " ")
        try:
            res = json.loads(json_src_replaced)
            return res
        except:
            pass

        if parse_options.correct_json_by_model:
            try:
                res = parse_json_by_cheap_model(json_src)
                return res
            except:
                pass

        raise ValueError(f"Invalid json: {src}")

    @staticmethod
    def list(src):
        # find first [
        start = src.find("[")
        # find last ]
        end = src.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"Invalid json: {src}")
        try:
            res = json.loads(src[start:end + 1])
        except:
            raise ValueError(f"Invalid json: {src}")
        return res

    @staticmethod
    def quotes(src: str):
        """
        Parse a string that is enclosed by quotes ```
        :param src:
        :return: contents of the quoted string
        """
        split_lines = src.split("\n")
        for start, line in enumerate(split_lines):
            if line.startswith("```"):
                title = line[3:]
                break
        else:
            raise ValueError("No closing quotes")
        for end in range(start + 1, len(split_lines)):
            if split_lines[end].startswith("```"):
                break
        else:
            raise ValueError("No closing quotes")
        contents = "\n".join(split_lines[start + 1: end])
        return contents

    @staticmethod
    def colon(src: str):
        """
        Parse a string that is separated by colons
        :param src:
        :return: the contents after the colon
        """
        split = src.split(":")
        if len(split) != 2:
            raise ValueError("Invalid colon string")
        contents = split[1].strip()
        return contents


def parse_json_by_cheap_model(json_src):
    """
    Correct a JSON dict with semantic errors using a model that support JSON model
    This is especially for claude models because they do not support JSON model
    :param json_src:
    :return:
    """
    from mllm import Chat
    prompt = f"""
You are required to correct a JSON dict with semantic errors. 
<raw_json>
{json_src}
</raw_json>
You should directly output the corrected JSON dict with a minimal modification.
"""
    chat = Chat(prompt)
    res = chat.complete(parse="dict", model=parse_options.cheap_model)
    return res
