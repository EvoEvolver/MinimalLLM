from mllm.config import default_models
from mllm.env_utils import check_replicate_env, check_anthropic_env, check_openai_env

def set_default_to_google():
    default_models["normal"] = "gemini-1.0-pro"
    default_models["expensive"] = "gemini-1.0-pro"
    default_models["vision"] = "gemini-1.0-pro-vision"
    default_models["embedding"] = "vertex_ai/textembedding-gecko"

def set_default_to_openai(use_gpt_4=False):
    check_openai_env()
    default_models["normal"] = "gpt-3.5-turbo"
    default_models["expensive"] = "gpt-4-turbo-preview" if not use_gpt_4 else "gpt-4"
    default_models["vision"] = "gpt-4-vision-preview"
    default_models["embedding"] = "text-embedding-3-large"

def set_default_to_anthropic(expensive_vision_model=False):
    check_anthropic_env()
    default_models["normal"] = "claude-3-sonnet-20240229"
    default_models["expensive"] = "claude-3-opus-20240229"
    default_models["vision"] = "claude-3-sonnet-20240229" if not expensive_vision_model else "claude-3-opus-20240229"
    default_models["embedding"] = "text-embedding-3-large"

def set_default_to_llama():
    check_replicate_env()
    default_models["normal"] = "replicate/meta/llama-2-13b-chat"
    default_models["expensive"] = "replicate/meta/llama-2-70b-chat"
    default_models["vision"] = "gpt-4-vision-preview"
    default_models["embedding"] = "text-embedding-3-large"