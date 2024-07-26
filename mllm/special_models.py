import os

from litellm import completion


def get_llava_response(messages, options, model_name):
    prompt, image = extract_prompt_and_image(messages)
    try:
        import replicate
    except ImportError:
        raise ImportError("Please install the `replicate` package to use the llava model")
    if os.environ["REPLICATE_API_TOKEN"] is None:
        if os.environ["REPLICATE_API_KEY"] is None:
            raise ValueError("Please set the REPLICATE_API_KEY environment variable")
        os.environ["REPLICATE_API_TOKEN"] = os.environ["REPLICATE_API_KEY"]
    model_name = model_name.split("/")[1:]
    model_name = "/".join(model_name)
    output = replicate.run(
        model_name,
        input={
            "image": image,
            "top_p": 1,
            "prompt": prompt,
            "history": [],
            "max_tokens": 2048,
            "temperature": options["temperature"],
        }
    )

    res = "".join(output)
    return res


def get_llama_response(messages, options, model_name):
    try:
        import replicate
    except ImportError:
        raise ImportError("Please install the `replicate` package to use the llava model")
    model_name = model_name.split("/")[1:]
    model_name = "/".join(model_name)
    prompt, image = extract_prompt_and_image(messages)
    output = replicate.run(
        model_name,
        input={
            "top_p": 1,
            "prompt": prompt,
            "history": [],
            "max_tokens": 2048*2,
            "temperature": options["temperature"],
        }
    )
    res = "".join(output)
    return res


def extract_prompt_and_image(messages):
    prompt = []
    image = None
    for message in messages:
        if message["role"] == "user":
            content = message["content"]
            if isinstance(content, str):
                prompt.append(content)
            else:
                for item in content:
                    if item["type"] == "text":
                        prompt.append(item["text"])
                    elif item["type"] == "image_url":
                        image = item["image_url"]["url"]
        else:
            content = message["content"] if isinstance(message["content"], str) else message["content"]["text"]
            prompt.append(f"<{message['role']}>" + content + f"<{message['role']}>")
    prompt = "\n".join(prompt)
    return prompt, image


special_models = {
    "replicate/yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174": get_llava_response
}


def get_special_model_handler(model_name):
    if not model_name.startswith("replicate/"):
        return None
    if "yorickvp/llava" in model_name:
        return lambda messages, options: get_llava_response(messages, options, model_name)
    if "llama" in model_name:
        return lambda messages, options: get_llama_response(messages, options, model_name)
