from dataclasses import dataclass


@dataclass
class DefaultModels:
    normal: str = "gpt-4o-mini"
    expensive: str = "gpt-4o"
    vision: str = "gpt-4o"
    embedding: str = "text-embedding-3-large"

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class DefaultOptions:
    temperature: float = 0.2
    max_tokens: int = None
    frequency_penalty: float = None
    timeout: int = 600
    seed: int = None

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


default_models = DefaultModels()

default_options = DefaultOptions()

if __name__ == '__main__':
    print(default_options.get_dict())
