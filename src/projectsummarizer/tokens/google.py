"""Google Gemini token counting utilities using local tokenization.

This module uses Vertex AI's local tokenization - vocabulary is downloaded once (~4MB)
and cached locally. Token counting works offline and does NOT send data to Google servers.

PRIVACY: Uses local tokenization only.

Blog post: https://dev.to/googlecloud/counting-gemini-text-tokens-locally-1oo1

Note: Gemini 2.0+ models use cloud-based tokenization APIs (not implemented here).
This module only supports Gemini 1.x models with local tokenization.
"""

from vertexai.preview.tokenization import get_tokenizer_for_model
import logging

logger = logging.getLogger(__name__)


def get_google_token_count(text: str, model_name: str) -> int:
    """
    Calculates the number of tokens in the given text for a Google Gemini model.

    PRIVACY: Uses LOCAL tokenization - downloads vocabulary file on first use (~4MB),
    then works offline. No text data is sent to Google servers.
    Reference: https://dev.to/googlecloud/counting-gemini-text-tokens-locally-1oo1

    Args:
        text: Text content to tokenize
        model_name: Google model name (e.g., 'gemini-1.5-flash-002')

    Returns:
        Number of tokens, or -1 if model is not found or there's an error
    """
    try:
        tokenizer = get_tokenizer_for_model(model_name)
        result = tokenizer.count_tokens(text)
        return result.total_tokens
    except ValueError as e:
        # Model not found or invalid model name
        logger.error(f"Google model '{model_name}' not found or invalid: {e}")
        return -1
    except Exception as e:
        # Other unexpected errors
        logger.error(f"Error counting tokens for Google model '{model_name}': {e}")
        return -1


def list_google_models():
    """
    Lists available Google Gemini models for offline tokenization.
    Returns a hardcoded list of supported models.
    """

    # Starting from gemini 2.0 models google moved them to the cloud
    # it requires an additional set up so for now we only support the older models
    # so use old models as an aproximation

    return [
        "gemini-1.0-pro-001",
        "gemini-1.0-pro-002",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-002",
    ]
