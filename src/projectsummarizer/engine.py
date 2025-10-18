from typing import List, Dict, Tuple, Optional
from projectsummarizer.files.tree.tree import FileSystemTree
from projectsummarizer.files.tree.node import FsNode
from projectsummarizer.files.discovery import IgnorePatternsHandler, FileScanner
from projectsummarizer.tokens import TokenCounter
from projectsummarizer.contents.readers import ContentReaderRegistry, TextFileReader, NotebookReader
from projectsummarizer.contents.readers.binary import BinaryFileReader
from projectsummarizer.plotting import TreePlotter


def _setup_file_discovery(
    directory: str,
    *,
    ignore_patterns: List[str] | None = None,
    use_defaults: bool = True,
    include_binary: bool = False,
    read_ignore_files: bool = True,
    token_counter = None,
    filter_type: str = "included",
) -> Tuple[IgnorePatternsHandler, FileScanner, Dict[str, Dict]]:
    """Set up file discovery components and return discovered file paths with files data."""
    scanner = FileScanner(
        root=directory,
        user_patterns=list(ignore_patterns or []),
        use_defaults=use_defaults,
        read_ignore_files=read_ignore_files,
        include_binary=include_binary,
        token_counter=token_counter,
        filter_type=filter_type
    )
    files_data = scanner.discover()
    return scanner.ignore_handler, scanner, files_data


def build_tree_from_directory(
    directory: str,
    *,
    ignore_patterns: List[str] | None = None,
    use_defaults: bool = True,
    include_binary: bool = False,
    read_ignore_files: bool = True,
    token_models: List[str] | None = None,
    filter_type: str = "included",
) -> FsNode:
    """Build a file tree from directory with ignore patterns and optional token counting."""
    # Set up token counter if models provided
    token_counter = None
    if token_models:
        token_counter = TokenCounter(token_models)
    
    _, _, files_data = _setup_file_discovery(
        directory,
        ignore_patterns=ignore_patterns,
        use_defaults=use_defaults,
        include_binary=include_binary,
        read_ignore_files=read_ignore_files,
        token_counter=token_counter,
        filter_type=filter_type,
    )
    
    # Create tree directly from files_data
    tree = FileSystemTree.from_files_data(files_data)
    return tree.root

def render_ascii_tree(root: FsNode) -> str:
    """Render ASCII tree with node statistics."""
    plotter = TreePlotter()
    return plotter.plot_ascii(root)


def build_summary(
    directory: str,
    *,
    ignore_patterns: List[str] | None = None,
    use_defaults: bool = True,
    include_binary: bool = False,
    read_ignore_files: bool = True,
    token_models: List[str] | None = None,
    max_file_size: int = 5*1024*1024,
    filter_type: str = "included",
) -> Tuple[FsNode, Dict[str, str]]:
    """Build tree with token counts and read file contents.
    
    Args:
        directory: Root directory to scan
        ignore_patterns: Additional ignore patterns
        use_defaults: Whether to use default ignore patterns
        include_binary: Whether to include binary files
        read_ignore_files: Whether to read .gitignore files
        token_models: List of models to count tokens for (e.g., ['gpt-4o'])
        max_file_size: Maximum file size to read (in bytes)
        
    Returns:
        (root_node, content_map) where content_map: {relpath: content}
    """
    # Set up token counter if models provided
    token_counter = None
    if token_models:
        token_counter = TokenCounter(token_models)
    
    # Get files data from discovery
    _, _, files_data = _setup_file_discovery(
        directory,
        ignore_patterns=ignore_patterns,
        use_defaults=use_defaults,
        include_binary=include_binary,
        read_ignore_files=read_ignore_files,
        token_counter=token_counter,
        filter_type=filter_type,
    )
    
    # Build tree from files data
    root = FileSystemTree.from_files_data(files_data).root
    
    # Set up content readers (specialized readers first, then fallback)
    reader_registry = ContentReaderRegistry()
    reader_registry.register(NotebookReader())  # Specialized reader for notebooks
    reader_registry.register(BinaryFileReader())  # Binary file reader
    reader_registry.register(TextFileReader())  # Fallback reader for all files
    
    # Read file contents with metadata
    content_map: Dict[str, str] = {}
    for relpath, file_data in files_data.items():
        full_path = f"{directory}/{relpath}"
        # Add relpath to file_data for the binary reader
        content = reader_registry.read(full_path, max_file_size, file_data)
        if content:  # Only include non-empty content
            content_map[relpath] = content
    
    return root, content_map
