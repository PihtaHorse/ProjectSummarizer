#!/usr/bin/env python3
"""List all available tokenizer models."""

import logging
from dotenv import load_dotenv
from projectsummarizer.tokens.openai import list_openai_models
from projectsummarizer.tokens.google import list_google_models
from projectsummarizer.tokens.anthropic import list_anthropic_models
from projectsummarizer.tokens.primitive import list_primitive_models

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(message)s')


def main():
    
    pairs = [
        ("OpenAI", list_openai_models), 
        ("Google", list_google_models), 
        ("Anthropic", list_anthropic_models),
        ("Primitive", list_primitive_models)
    ]

    for name, list_models in pairs:
        print(f"{name} Models:")
        try:
            models_list = list_models()
            for model in models_list:
                print(f"   {model}")
        except Exception as e:
            print(f"Error listing {name} models: {e}")


if __name__ == "__main__":
    main()
