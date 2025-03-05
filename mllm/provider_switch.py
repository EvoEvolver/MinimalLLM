from mllm.config import default_models
from mllm.env_utils import check_replicate_env, check_anthropic_env, check_openai_env

def set_default_to_deepseek():
    default_models["normal"] = "deepseek/deepseek-chat"
    default_models["expensive"] = "deepseek/deepseek-chat"
    default_models["vision"] = "gpt-4o"
    default_models["embedding"] = "text-embedding-3-large"


def set_default_to_gemini():
    default_models["normal"] = "gemini/gemini-pro"
    default_models["expensive"] = "gemini/gemini-1.5-pro-latest"
    default_models["vision"] = "gemini/gemini-1.5-pro-latest"
    default_models["embedding"] = "text-embedding-3-large"

def set_default_to_openai():
    check_openai_env()
    default_models["normal"] = "gpt-4o-mini"
    default_models["expensive"] = "gpt-4o"
    default_models["vision"] = "gpt-4o"
    default_models["embedding"] = "text-embedding-3-large"

def set_default_to_anthropic(expensive_vision_model=False):
    check_anthropic_env()
    default_models["normal"] = "claude-3-7-sonnet-20250219"
    default_models["expensive"] = "claude-3-opus-20240229"
    default_models["vision"] = "claude-3-7-sonnet-20250219" if not expensive_vision_model else "claude-3-opus-20240229"
    default_models["embedding"] = "text-embedding-3-large"

def set_default_to_llama():
    check_replicate_env()
    default_models["normal"] = "replicate/meta/meta-llama-3-70b-instruct"
    default_models["expensive"] = "replicate/meta/meta-llama-3-70b-instruct"
    default_models["vision"] = "replicate/yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174"
    default_models["embedding"] = "text-embedding-3-large"