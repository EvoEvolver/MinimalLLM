

def get_llava_response(messages, options, model_name):
    image, prompt = extract_prompt_and_image(messages)
    try:
        import replicate
    except ImportError:
        raise ImportError("Please install the `replicate` package to use the llava model")
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


def extract_prompt_and_image(messages):
    prompt = []
    image = None
    for message in messages:
        if message["role"] == "user":
            for item in message["content"]:
                if item["type"] == "text":
                    prompt.append(item["text"])
                elif item["type"] == "image_url":
                    image = item["image_url"]["url"]
        elif message["role"] == "system":
            prompt.append("<system>" + message["content"] + "</system>")
    prompt = "\n".join(prompt)
    return image, prompt


special_models = {
    "replicate/yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174": get_llava_response
}

def get_special_model_handler(model_name):
    handler = special_models.get(model_name, None)
    if handler is not None:
        return lambda messages, options: handler(messages, options, model_name)
    return None




