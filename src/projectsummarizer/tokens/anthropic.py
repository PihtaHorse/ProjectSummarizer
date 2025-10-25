"""Anthropic token counting utilities.

PRIVACY WARNING: This module makes API calls to Anthropic servers.
When you use Anthropic models for token counting, your code content is sent to
Anthropic's external servers. This is NOT a local operation.

DO NOT use with confidential, proprietary, or corporate code.

For safe local-only token counting, use:
- Character-based tokenizer: chars-4
- OpenAI tokenizer: gpt-4o (appears local based on tiktoken library)
- Google Gemini tokenizer: gemini-1.5-flash-002 (confirmed local)
"""

import logging
import anthropic
import os

logger = logging.getLogger(__name__)


def get_anthropic_api_key():
    # Unfortunately you need to have a api key to use this, 
    # you can get it from here: https://console.anthropic.com/settings/keys
    # Last time I tried it wasn't free
    
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise RuntimeError("CLAUDE_API_KEY is not set. Please configure it in your .env file.")
    return api_key

def get_anthropic_token_count(messages, model_name):
    """
    Calculates the number of tokens in the given messages for an Anthropic model.
    Note: This makes an API call to Anthropic servers and requires CLAUDE_API_KEY.

    Privacy NOTE: This function DOES NOT operate LOCALLY. It sends the text to Anthropic servers to count the tokens.
    Use with caution.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model_name: Anthropic model name (e.g., 'claude-sonnet-4-5-20250929')

    Returns:
        Number of tokens, or -1 if there's an error

    Raises:
        RuntimeError: If CLAUDE_API_KEY is not set (re-raised from get_anthropic_api_key)
    """
    # Check if messages are empty or all have empty content
    if not messages or all(not msg.get("content", "").strip() for msg in messages):
        return 0

    try:
        client = anthropic.Anthropic(api_key=get_anthropic_api_key())
        return client.messages.count_tokens(model=model_name, messages=messages).input_tokens
    except RuntimeError:
        # API key not set - re-raise with context
        raise RuntimeError(
            f"CLAUDE_API_KEY is required for counting tokens with Anthropic models. "
            f"Please set it in your .env file. See: https://console.anthropic.com/settings/keys"
        )
    except anthropic.NotFoundError as e:
        # Model not found
        logger.error(f"Anthropic model '{model_name}' not found: {e}")
        return -1
    except anthropic.BadRequestError as e:
        # Invalid request (shouldn't happen with our empty check, but just in case)
        logger.error(f"Bad request for Anthropic model '{model_name}': {e}")
        return -1
    except Exception as e:
        # Other unexpected errors
        logger.error(f"Error counting tokens for Anthropic model '{model_name}': {e}")
        return -1


def list_anthropic_models():
    """
    Lists available Anthropic models.
    """
    client = anthropic.Anthropic(api_key=get_anthropic_api_key())
    models = client.models.list()

    return sorted([model.id for model in models])
