"""Token counting orchestrator for various AI models."""

from typing import Dict, List
from projectsummarizer.tokens.openai import get_openai_token_count
from projectsummarizer.tokens.anthropic import get_anthropic_token_count
from projectsummarizer.tokens.google import get_google_token_count
from projectsummarizer.tokens.primitive import get_primitive_token_count
import logging

logger = logging.getLogger(__name__)


class TokenCounter:
    """Orchestrates token counting for content using various models."""

    # Model prefix to provider mapping
    OPENAI_PREFIXES = ("gpt-", "o1-")
    GOOGLE_PREFIXES = ("gemini-", "palm-")
    ANTHROPIC_PREFIXES = ("claude-",)
    PRIMITIVE_PREFIXES = ("chars-",)

    def __init__(self, models: List[str]):
        """Initialize with list of model names (e.g., ['gpt-4o'])."""
        self.models = models

    def _get_provider_for_model(self, model: str) -> str:
        """Determine the provider based on model name prefix.

        Args:
            model: Model name to check

        Returns:
            Provider name: 'openai', 'google', 'anthropic', 'primitive', or 'unknown'
        """
        if model.startswith(self.OPENAI_PREFIXES):
            return "openai"
        elif model.startswith(self.GOOGLE_PREFIXES):
            return "google"
        elif model.startswith(self.ANTHROPIC_PREFIXES):
            return "anthropic"
        elif model.startswith(self.PRIMITIVE_PREFIXES):
            return "primitive"
        else:
            return "unknown"

    def count_tokens(self, content: str) -> Dict[str, int]:
        """Return token counts per model: {model_name: count}.

        Args:
            content: Text content to count tokens for

        Returns:
            Dictionary mapping model names to token counts

        Raises:
            ValueError: If model prefix is unknown or model is not supported
            RuntimeError: If API credentials are not configured
        """
        counts: Dict[str, int] = {}

        for model in self.models:
            provider = self._get_provider_for_model(model)

            if provider == "unknown":
                raise ValueError(
                    f"Unknown model prefix for '{model}'. "
                    f"Supported prefixes: {self.OPENAI_PREFIXES}, {self.ANTHROPIC_PREFIXES}, {self.GOOGLE_PREFIXES}, {self.PRIMITIVE_PREFIXES}"
                )

            if provider == "openai":
                token_count = get_openai_token_count(content, model)
            elif provider == "anthropic":
                # Anthropic requires messages format
                token_count = get_anthropic_token_count(
                    [{"role": "user", "content": content}], model
                )
            elif provider == "google":
                token_count = get_google_token_count(content, model)
            elif provider == "primitive":
                token_count = get_primitive_token_count(content, model)

            # Check if the token counting failed (returned -1)
            if token_count < 0:
                raise ValueError(
                    f"Failed to count tokens for model '{model}'. "
                    f"The model may not exist or may not be supported by the {provider} tokenizer."
                )

            counts[model] = token_count

        return counts
