"""Primitive character-based token counting utilities.

This module provides a simple, estimation-based tokenizer that operates 100% locally
with NO external dependencies, NO downloads, and NO API calls. It estimates tokens
based on a configurable characters-per-token ratio.

PRIVACY: Completely local operation. No data is sent anywhere. No external dependencies.
"""

import logging
import math

logger = logging.getLogger(__name__)


def get_primitive_token_count(text: str, model_name: str) -> int:
    """
    Estimates the number of tokens based on characters-per-token ratio.

    PRIVACY: This function operates 100% LOCALLY with no external dependencies.
    It simply divides character count by the specified ratio.

    Model name format: "chars-{ratio}" where ratio is chars-per-token.
    Examples: "chars-4" (4 chars/token), "chars-3.5" (3.5 chars/token)

    Args:
        text: Text content to tokenize
        model_name: Model name in format "chars-{ratio}" (e.g., "chars-4")

    Returns:
        Number of tokens (rounded up), or -1 if model name is invalid
    """
    # Parse the ratio from model name
    if not model_name.startswith("chars-"):
        logger.error(f"Invalid chars model name: '{model_name}'. Expected format: 'chars-{{ratio}}'")
        return -1

    try:
        ratio_str = model_name.replace("chars-", "")
        chars_per_token = float(ratio_str)

        if chars_per_token <= 0:
            logger.error(f"Invalid chars-per-token ratio: {chars_per_token}. Must be positive.")
            return -1

        # Calculate token count: divide character count by ratio, round up
        token_count = math.ceil(len(text) / chars_per_token)
        return token_count

    except ValueError as e:
        logger.error(f"Invalid chars model name: '{model_name}'. Could not parse ratio: {e}")
        return -1
    except Exception as e:
        logger.error(f"Error counting tokens for chars model '{model_name}': {e}")
        return -1


def list_primitive_models():
    """
    Lists available character-based tokenization models.

    Returns a list of common character-per-token ratios. Users can use any positive
    number in the format "chars-{ratio}", but these are typical values:
    - chars-1 : ~1 character per token (just characters)
    - chars-4: ~4 characters per token (common default, similar to GPT models)

    Any positive float ratio is supported (e.g., chars-2.7, chars-10).
    """
    return [
        "chars-1",
        "chars-4",
    ]
