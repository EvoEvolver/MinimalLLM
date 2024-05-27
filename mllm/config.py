
default_models = {
    "normal": "gpt-3.5-turbo",
    "expensive": "gpt-4-turbo-preview",
    "vision": "gpt-4-vision-preview",
    "embedding": "text-embedding-3-large"
}


default_options = {
    "temperature": 0.2,
    "max_tokens": None,
    "frequency_penalty": None,
    "timeout": 600,
    "seed": None,
}


class CacheOptions:
    def __init__(self):
        self.max_embedding_vecs = 1000
        self.max_chat = 1000