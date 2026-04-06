"""Content I/O operations - reading file contents and writing formatted output."""

from projectsummarizer.contents.readers import ContentReaderRegistry, TextFileReader, NotebookReader, BinaryFileReader
from projectsummarizer.contents.formatters import (
    BaseFormatter,
    StreamingTextFormatter,
    XMLFormatter,
    MarkdownFormatter,
    create_formatter,
)

__all__ = [
    "ContentReaderRegistry",
    "TextFileReader",
    "NotebookReader",
    "BinaryFileReader",
    "BaseFormatter",
    "StreamingTextFormatter",
    "XMLFormatter",
    "MarkdownFormatter",
    "create_formatter",
]
