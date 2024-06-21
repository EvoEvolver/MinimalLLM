import ast
import json

"""
# Parse
"""

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
        except:
            try:
                res = ast.literal_eval(json_src)
            except:
                raise ValueError(f"Invalid json/dict: {src}")
        return res

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
        for end in range(start+1, len(split_lines)):
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
