from typing import List, Dict
from ..token_handlers.openai_token_handler import get_openai_token_count
from ..token_handlers.anthropic_token_handler import get_anthropic_token_count


def get_all_content_counts(content: str, models: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {"characters": len(content)}

    if "gpt-4o" in models:
        counts["gpt-4o"] = get_openai_token_count(content, "gpt-4o")

    if "claude-3-5-sonnet-20241022" in models:
        counts["claude-3-5-sonnet-20241022"] = get_anthropic_token_count(
            [{"role": "user", "content": content}], "claude-3-5-sonnet-20241022"
        )

    return counts


