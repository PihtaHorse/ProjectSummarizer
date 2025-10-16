"""Token counting orchestrator for various AI models."""

from typing import Dict, List
from .openai import get_openai_token_count
from .anthropic import get_anthropic_token_count


class TokenCounter:
    """Orchestrates token counting for content using various models."""
    
    def __init__(self, models: List[str]):
        """Initialize with list of model names (e.g., ['gpt-4o'])."""
        self.models = models
    
    def count_tokens(self, content: str) -> Dict[str, int]:
        """Return token counts per model: {model_name: count}.
        
        Args:
            content: Text content to count tokens for
            
        Returns:
            Dictionary mapping model names to token counts
        """
        counts: Dict[str, int] = {"characters": len(content)}
        
        for model in self.models:
            if model == "gpt-4o":
                counts["gpt-4o"] = get_openai_token_count(content, "gpt-4o")
            elif model == "claude-3-5-sonnet-20241022":
                counts["claude-3-5-sonnet-20241022"] = get_anthropic_token_count(
                    [{"role": "user", "content": content}], "claude-3-5-sonnet-20241022"
                )
        
        return counts
