"""Anthropic token counting utilities."""

import anthropic
import os


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
    """
    client = anthropic.Anthropic(api_key=get_anthropic_api_key())
    return client.messages.count_tokens(model=model_name, messages=messages).input_tokens


def list_anthropic_models():
    """
    Lists available Anthropic models.
    """
    client = anthropic.Anthropic(api_key=get_anthropic_api_key())
    for model in client.models.list():
        print(f"Anthropic Model ID: {model.id}")
