"""ProjectSummarizer - A tool to summarize project files with tree view and analysis.

This package provides functionality to:
- Discover and scan files in a directory
- Build filesystem trees with metrics
- Count tokens for various LLM models
- Generate formatted summaries of projects
- Visualize directory structures as ASCII trees
"""

from projectsummarizer.engine import (
    build_tree_from_directory,
    build_summary,
    render_ascii_tree,
)

from projectsummarizer.files.tree.node import FileSystemNode
from projectsummarizer.files.tree.tree import FileSystemTree
from projectsummarizer.files.discovery import (
    FileDiscoverer,
    IgnorePatternsHandler,
    BinaryDetector,
)
from projectsummarizer.tokens import TokenCounter
from projectsummarizer.contents.readers import (
    ContentReaderRegistry,
    BaseContentReader,
    TextFileReader,
    NotebookReader,
)
from projectsummarizer.contents.formatters import (
    BaseFormatter,
    TextFormatter,
)
from projectsummarizer.plotting import TreePlotter

__version__ = "0.1.0"

__all__ = [
    # Main API functions
    "build_tree_from_directory",
    "build_summary",
    "render_ascii_tree",

    # Core classes
    "FileSystemNode",
    "FileSystemTree",
    "FileDiscoverer",
    "IgnorePatternsHandler",
    "BinaryDetector",
    "TokenCounter",

    # Content handling
    "ContentReaderRegistry",
    "BaseContentReader",
    "TextFileReader",
    "NotebookReader",

    # Formatters
    "BaseFormatter",
    "TextFormatter",

    # Visualization
    "TreePlotter",

    # Version
    "__version__",
]
