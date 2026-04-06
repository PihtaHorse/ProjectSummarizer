"""Output formatters for different summary formats."""

from projectsummarizer.contents.formatters.base import BaseFormatter
from projectsummarizer.contents.formatters.text_formatter import StreamingTextFormatter
from projectsummarizer.contents.formatters.xml_formatter import XMLFormatter
from projectsummarizer.contents.formatters.markdown_formatter import MarkdownFormatter


def create_formatter(format: str, output_path: str, **kwargs) -> BaseFormatter:
    """Factory function to create the appropriate formatter.

    Args:
        format: Output format — 'text', 'xml', or 'markdown'
        output_path: Path to the output file to create/overwrite
        **kwargs: Additional arguments passed to the formatter (e.g. delimiter for text format)

    Returns:
        A BaseFormatter instance for the requested format
    """
    if format == "xml":
        return XMLFormatter(output_path)
    elif format == "markdown":
        return MarkdownFormatter(output_path)
    else:  # "text"
        return StreamingTextFormatter(output_path, **kwargs)


__all__ = [
    "BaseFormatter",
    "StreamingTextFormatter",
    "XMLFormatter",
    "MarkdownFormatter",
    "create_formatter",
]
