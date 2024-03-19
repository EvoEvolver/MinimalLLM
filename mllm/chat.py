from __future__ import annotations

import base64
import copy
import html
from io import BytesIO

import httpx
from PIL.Image import Image
from litellm import completion

from mllm.cache.cache_service import caching
from mllm.debug.logger import Logger
from mllm.config import default_models
from mllm.debug.show_table import show_json_table


def encode_image(image_file: BytesIO):
    return base64.b64encode(image_file.read()).decode('utf-8')


class ChatLogger(Logger):
    active_loggers = []

    def display_log(self):
        contents = [str(chat) for chat in self.log_list]
        filenames = [caller_name.split("/")[-1] for caller_name in self.caller_list]
        info_list = []
        for i in range(len(contents)):
            content = html.escape(contents[i])
            content = content.replace("\n", "<br/>")
            info_list.append({
                "filename": filenames[i],
                "content": content
            })
        show_json_table(info_list)

class Chat:
    """
    Class for chat completion
    """

    def __init__(self, user_message=None, system_message: any = None):
        self.messages = []
        self.system_message = system_message
        if user_message is not None:
            self._add_message(user_message, "user")

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
        self._add_image_message(base64_image, media_type, more)

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
                "content": [{
                    "type": "text",
                    "text": self.system_message
                }]
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

        return messages

    def contains_image(self):
        for message in self.messages:
            content = message["content"]
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item["type"] == "image":
                        return True
            elif isinstance(content, dict):
                if content["type"] == "image":
                    return True
        return False

    """
    ## Chat completion functions
    """

    def complete(self, model=None, cache=False, options=None):
        if options is None:
            options = {}
        if model is None:
            model = default_models["normal"]
            if self.contains_image():
                model = default_models["vision"]
        return self._complete_chat_impl(model, cache, options)

    def complete_expensive(self, model=None, cache=False, options=None):
        if options is None:
            options = {}
        if model is None:
            model = default_models["expensive"]
            if self.contains_image():
                model = default_models["vision"]
        return self._complete_chat_impl(model, cache, options)

    def _complete_chat_impl(self, model: str, use_cache: bool, options):
        messages = self.get_messages_to_api()
        if use_cache:
            cache = caching.cache_kv.read_cache(messages, "chat")
            if cache is not None and cache.is_valid():
                self.add_assistant_message(cache.value)
                return cache.value

        options = options or {}

        res = completion(model, messages=messages, **options).choices[0].message.content

        if len(ChatLogger.active_loggers) > 0:
            for chat_logger in ChatLogger.active_loggers:
                chat_logger.add_log(self)
        self.add_assistant_message(res)

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
            content = []
            for item in entry["content"]:
                if item["type"] == "text":
                    content.append(item["text"])
                elif item["type"] == "image":
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
