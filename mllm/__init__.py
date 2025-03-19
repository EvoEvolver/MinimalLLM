import os
import warnings

from mllm.chat import Chat
from mllm.cache.cache_service import caching
from mllm.embedding import get_embeddings
from mllm.debug import display_chats

import dotenv
dotenv_loaded = False
if not dotenv_loaded:
    dotenv_loaded = True
    dotenv_file = dotenv.find_dotenv(".mllm.env", raise_error_if_not_found=False)
    if dotenv_file:
        dotenv.load_dotenv(dotenv_file, override=True)

import litellm
if "LITELLM_API_KEY" in os.environ:
    if "LITELLM_API_BASE" in os.environ:
        litellm.api_key = os.environ["LITELLM_API_KEY"]
        litellm.api_base = os.environ["LITELLM_API_BASE"]
    else:
        warnings.warn("LITELLM_API_BASE not found in environment variable though LITELLM_API_KEY is found")