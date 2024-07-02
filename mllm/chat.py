from __future__ import annotations

import base64
import copy
import html
import textwrap
from io import BytesIO

import httpx
from PIL.Image import Image
from litellm import completion, get_llm_provider

from mllm.cache.cache_service import caching
from mllm.utils.logger import Logger
from mllm.config import default_models, default_options
from mllm.display.show_html import show_json_table
from mllm.utils.parser import Parse

n_chat_retry = 3

def encode_image(image_file: BytesIO):
    return base64.b64encode(image_file.read()).decode('utf-8')


def get_chat_in_html(chat: Chat):
    res = []
    message_to_api = chat.get_messages_to_api()
    for entry in message_to_api:
        if isinstance(entry["content"], str):
            entry["content"] = [{"type": "text", "text": entry["content"]}]
        content = []
        for item in entry["content"]:
            if item["type"] == "text":
                text = item["text"]
                text = html.escape(text)
                text = text.replace("\n", "<br/>")
                text = text.replace(" ", "&nbsp;")
                content.append(text)
            elif item["type"] == "image_url":
                content.append("<image src='{}' style='max-height: 200px;'/>".format(item["image_url"]["url"]))
        content = "<br/>".join(content)
        res.append(f"------{entry['role']}------<br/> {content}")
    return "<br/>".join(res)

class ChatLogger(Logger):
    active_loggers = []

    def display_log(self):
        contents = [get_chat_in_html(chat) for chat in self.log_list]
        filenames = [caller_name.split("/")[-1] for caller_name in self.caller_list]
        info_list = []
        for i in range(len(contents)):
            content = contents[i]
            info_list.append({
                "filename": filenames[i],
                "content": content
            })
        show_json_table(info_list)


class ParseError(Exception):
    pass


def parse_res(parse, res):
    if parse not in ["dict", "list", "obj", "quotes", "colon"]:
        raise ValueError("Invalid parse type")
    try:
        res = Parse.__dict__[parse](res)
    except Exception as e:
        raise ParseError(f"Failed to parse the result: {e}")
    return res


class Chat:
    """
    Class for chat completion
    """

    def __init__(self, user_message=None, system_message: any = None, dedent=True):
        """
        Create a new chat session. You can get the completion result by calling the `complete` method.
        :param user_message: the first message from the user
        :param system_message: the system message
        :param dedent: whether to dedent the user message automatically
        """
        self.messages = []
        self.system_message = system_message
        if user_message is not None:
            self._add_message(user_message, "user")
        self.dedent = dedent

    """
    ## Message editing and output
    """

    def _add_message(self, content: any, role: str):
        self.messages.append({
            "role": role,
            "content": {
                "type": "text",
                "text": content
            }
        })

    def _add_image_message(self, data: str, media_type: str):
        self.messages.append({
            "role": "user",
            "content": {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{media_type};base64,{data}"
                }
            }
        })

    def add_user_message(self, content: any):
        if self.dedent:
            content = textwrap.dedent(content).strip()
        self._add_message(content, "user")

    def add_image_message(self, image_or_image_path: str | Image, more: dict = None):
        """
        :param image_path: The path of the image
        """

        if isinstance(image_or_image_path, str):
            from_internet = image_or_image_path.startswith(
                "http://") or image_or_image_path.startswith("https://")
            if not from_internet:
                img_io = open(image_or_image_path, "rb")
            else:
                img_io = BytesIO(httpx.get(image_or_image_path).content)
            media_type = image_or_image_path.split(".")[-1]
            media_type = media_type.lower()
            base64_image = encode_image(img_io)
        else:
            img_io = BytesIO()
            image_or_image_path.save(img_io, format="png")
            media_type = "png"
            base64_image = base64.b64encode(img_io.getvalue()).decode('utf-8')

        assert media_type in ["jpg", "jpeg", "png", "gif", "webp"]
        if media_type == "jpg":
            media_type = "jpeg"

        img_io.close()
        self._add_image_message(base64_image, media_type)

    def add_assistant_message(self, content: any):
        self._add_message(content, "assistant")

    def get_messages_to_api(self):
        """
        :return: messages for sending to model APIs
        """
        messages = []
        if self.system_message is not None:
            messages.append({
                "role": "system",
                "content": self.system_message
            })

        if len(self.messages) == 0:
            return messages

        content_list = []
        curr_role = self.messages[0]["role"]
        content_dict = {
            "role": curr_role,
            "content": content_list
        }
        messages.append(content_dict)

        for message in self.messages:
            if message["role"] != curr_role:
                content_list = []
                curr_role = message["role"]
                content_dict = {
                    "role": curr_role,
                    "content": content_list
                }
                messages.append(content_dict)
            content_list.append(message["content"])

        # Merge text messages into one
        for message in messages:
            if message["role"] != "user":
                continue
            content_list = []
            merge_failed = False
            for item in message["content"]:
                if item["type"] == "text":
                    content_list.append(item["text"])
                else:
                    merge_failed = True
                    break
            if not merge_failed:
                message["content"] = "\n".join(content_list)

        return messages

    def contains_image(self):
        for message in self.messages:
            content = message["content"]
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item["type"] == "image":
                        return True
            elif isinstance(content, dict):
                if "image_url" in content:
                    return True
        return False

    """
    ## Chat completion functions
    """

    def complete(self, model=None, cache=False, expensive=False, parse=None, retry=True, options=None):
        """
        :param model: The name of the model to use. If None, the default model will be used.
        :param cache: Whether to use cache. If True, the result will be cached.
        :param expensive: Whether to use the expensive model. If True, the default expensive model will be used.
        :param parse: How to parse the result. Options: "dict", "list", "obj", "quotes", "colon". See http://mllm.evoevo.org/parsing for details.
        :param retry: Whether to retry if the completion fails.
        :param options: Additional options for the completion model.
        :return: The completion result from the model. If parse is set, a parsed result will be returned.
        """
        if options is None:
            options = {}
        options = {**default_options, **options}
        if model is None:
            if not expensive:
                model = default_models["normal"]
            else:
                model = default_models["expensive"]
            if self.contains_image():
                model = default_models["vision"]

        if get_llm_provider(model)[1] in ["openai", "anthropic"]:
            if parse == "dict":
                options["response_format"] = { "type": "json_object" }

        for n_tries in range(n_chat_retry):
            try:
                res = self._complete_chat_impl(model, cache, options)
                if parse is not None:
                    res = parse_res(parse, res)
                return res
            # Retry if the completion fails on TimeoutError or ParseError
            except (TimeoutError, ParseError) as e:
                if not retry:
                    raise e
                # Disable cache for retry
                cache = False
                print(e)
                # print stack here
                import traceback
                print(traceback.format_exc())
                print("Retrying...")
        raise Exception("Failed to complete chat. Did you set the correct API key? Did you prompt the model to output the expected parsing format?")

    def _complete_chat_impl(self, model: str, use_cache: bool, options):
        messages = self.get_messages_to_api()
        if use_cache:
            cache = caching.cache_kv.read_cache(messages, "chat")
            if cache is not None and cache.is_valid():
                self.add_assistant_message(cache.value)
                ChatLogger.add_log_to_all(self, stack_depth=2)
                return cache.value

        options = options or {}

        res = completion(model, messages=messages, **options).choices[0].message.content

        self.add_assistant_message(res)

        ChatLogger.add_log_to_all(self, stack_depth=2)

        if use_cache and cache is not None:
            cache.set_cache(res)
        return res

    """
    ## Magic methods
    """

    def __str__(self):
        res = []
        message_to_api = self.get_messages_to_api()
        for entry in message_to_api:
            if isinstance(entry["content"], str):
                content = entry["content"]
            else:
                content = []
                for item in entry["content"]:
                    if item["type"] == "text":
                        content.append(item["text"])
                    elif item["type"] == "image_url":
                        content.append("<image/>")
                content = "\n".join(content)
            res.append(f"------{entry['role']}------\n {content}")
        return "\n".join(res)

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.system_message!r}"

    def __copy__(self):
        new_chat = Chat(system_message=self.system_message)
        new_chat.messages = copy.deepcopy(self.messages)
        return new_chat

    def __add__(self, other):
        assert isinstance(other, str)
        self.add_user_message(other)
        return self
