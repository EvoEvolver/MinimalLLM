from __future__ import annotations

import base64
import copy
import time
from io import BytesIO

import httpx
from PIL.Image import Image
from litellm import completion, get_llm_provider

from mllm.cache.cache_service import caching
from mllm.chat_logger import ChatLogger
from mllm.special_models import get_special_model_handler
from mllm.config import default_models, default_options
from mllm.utils.parser import Parse

n_chat_retry = 3


def encode_image(image_file: BytesIO):
    return base64.b64encode(image_file.read()).decode('utf-8')


class ParseError(Exception):
    pass


def parse_res(parse, res):
    if parse not in ["dict", "list", "obj", "quotes", "colon"]:
        raise ValueError("Invalid parse type")
    try:
        res = Parse.__dict__[parse].__func__(res)
    except Exception as e:
        raise ParseError(f"Failed to parse the result: {e}\nInput to parse: {res}")
    return res


class Chat:
    """
    Class for chat completion
    """

    def __init__(self, user_message=None, system_message: any = None, dedent=False):
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
        self.additional_res = None

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

    def _pop_message(self):
        return self.messages.pop()

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
                    text = item["text"]
                    if self.dedent:
                        text = remove_all_indents(text)
                    content_list.append(text)
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

    def complete(self, model=None, cache=False, expensive=False, parse=None, retry=True,
                 options=None):
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
        options = {**default_options.get_dict(), **options}

        contains_image = self.contains_image()
        if model is None:
            if not expensive:
                model = default_models.normal
            else:
                model = default_models.expensive
            if contains_image:
                model = default_models.vision

        if get_llm_provider(model)[1] in ["openai", "deepseek"]:
            if parse == "dict":
                if not contains_image or model == "gpt-4o":
                    options["response_format"] = {"type": "json_object"}

        for n_tries in range(n_chat_retry):
            try:
                res, additional_res = self._complete_chat_impl(model, cache, options)
                self.add_assistant_message(res)
                ChatLogger.add_log_to_all((self.get_messages_to_api(), additional_res), stack_depth=1)
                try:
                    if parse is not None:
                        final_res = parse_res(parse, res)
                    else:
                        final_res = res
                except ParseError as e:
                    self._pop_message()
                    raise e
                self.additional_res = additional_res
                return final_res
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
                time.sleep(2.0)
        raise Exception(
            "Failed to complete chat. Did you set the correct API key? Did you prompt the model to output the expected parsing format?")

    def _complete_chat_impl(self, model: str, use_cache: bool, options):
        messages = self.get_messages_to_api()
        mock_response = None
        cache = None
        additional_res = {}
        if use_cache:
            cache = caching.read_kv_cache(messages, "chat_"+model)
            if cache is not None and cache.is_valid():
                mock_response = cache.value
                additional_res["cache_hit"] = True
                # Avoid unnecessary cache rewriting
                use_cache = False

        options = options or {}
        special_handler = get_special_model_handler(model)
        if special_handler is None:
            response = completion(model, messages=messages, mock_response=mock_response, **options)
            res = response.choices[0].message.content
            usage = response.model_extra["usage"]
            additional_res["prompt_tokens"] = usage.prompt_tokens
            additional_res["completion_tokens"] = usage.completion_tokens
            additional_res["full_message"] = response.choices[0].message
        else:
            res = special_handler(messages, options)
        if use_cache and cache is not None:
            cache.set_cache(res)
        return res, additional_res

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
        return f"Chat({self.get_messages_to_api()})"

    def __copy__(self):
        new_chat = Chat(system_message=self.system_message)
        new_chat.messages = copy.deepcopy(self.messages)
        return new_chat

    def __add__(self, other):
        assert isinstance(other, str)
        self.add_user_message(other)
        return self


def remove_all_indents(text: str):
    # Remove all leading indents at each line
    lines = text.split("\n")
    lines = [line.lstrip() for line in lines]
    return "\n".join(lines)
