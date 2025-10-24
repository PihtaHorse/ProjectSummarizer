"""OpenAI token counting utilities."""

import logging
import tiktoken
from tiktoken.model import MODEL_TO_ENCODING, MODEL_PREFIX_TO_ENCODING

logger = logging.getLogger(__name__)


def get_openai_token_count(text: str, model_name: str) -> int:
    """
    Calculates the number of tokens in the given text for an OpenAI model.
    """
    try:
        enc = tiktoken.encoding_for_model(model_name)
        tokens = enc.encode(text)
        return len(tokens)
    except KeyError:
        logger.error(f"Model '{model_name}' not found.")
        return -1


def list_openai_models():
    """
    Lists available OpenAI models and encodings.
    """

    logger.info("OpenAI Model names:")
    for model_name in MODEL_TO_ENCODING:
        logger.info(f"   {model_name}")
    logger.info("OpenAI Model prefixes:")
    for model_prefix in MODEL_PREFIX_TO_ENCODING:
        logger.info(f"   {model_prefix}")
