"""OpenAI token counting utilities.

This module uses tiktoken, an open-source BPE tokenizer library. Based on the code
structure (no API endpoints) and OpenAI Cookbook documentation (downloads encoding
files once, then works offline), tokenization appears to operate locally.

Official source: https://github.com/openai/tiktoken
Cookbook: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
(Search for "internet connection")
"""

import logging
import tiktoken
from tiktoken.model import MODEL_TO_ENCODING, MODEL_PREFIX_TO_ENCODING


logger = logging.getLogger(__name__)


def get_openai_token_count(text: str, model_name: str) -> int:
    """
    Calculates the number of tokens in the given text for an OpenAI model.

    PRIVACY NOTE: tiktoken is an open-source library that downloads encoding files
    once and then works offline (per OpenAI Cookbook). The codebase contains no API
    client or server endpoints, suggesting local operation.
    References: https://github.com/openai/tiktoken (source code)
                https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken (search for "internet connection" in the text)

    Args:
        text: Text content to tokenize
        model_name: OpenAI model name (e.g., 'gpt-4o')

    Returns:
        Number of tokens, or -1 if model is not found
    """
    try:
        enc = tiktoken.encoding_for_model(model_name)
        tokens = enc.encode(text)
        return len(tokens)
    except KeyError:
        # Model not found in tiktoken's registry
        logger.error(f"OpenAI model '{model_name}' not found in tiktoken registry")
        return -1
    except Exception as e:
        logger.error(f"Error counting tokens for OpenAI model '{model_name}': {e}")
        return -1


def list_openai_models():
    """
    Lists available OpenAI models and encodings.
    """

    encoding_models = [model_name for model_name in MODEL_TO_ENCODING]
    prefix_models = [model_prefix for model_prefix in MODEL_PREFIX_TO_ENCODING]
    models = encoding_models + prefix_models

    filtered_models = [
        model for model in models 
        if model.startswith("gpt-") or model.startswith("o1-")
    ]
    return sorted(list(set(filtered_models)))
