from typing import List, Optional, Callable
from projectsummarizer.files.tree.tree import FileSystemTree
from projectsummarizer.files.tree.node import FileSystemNode
from projectsummarizer.files.discovery import FileDiscoverer
from projectsummarizer.tokens import TokenCounter
from projectsummarizer.plotting import TreePlotter


def build_tree(
    directory: str,
    *,
    ignore_patterns: List[str] | None = None,
    use_defaults: bool = True,
    include_binary: bool = False,
    read_ignore_files: bool = True,
    token_models: List[str] | None = None,
    filter_type: str = "included",
    content_processor: Optional[Callable[[str, str], None]] = None,
    level: Optional[int] = None,
    include_dates: bool = False,
) -> FileSystemNode:
    """Build a file tree from directory with optional token counting and content streaming.

    This is the unified function for building file trees. It reads each file exactly once,
    making it memory-efficient for large projects.

    Args:
        directory: Root directory to scan
        ignore_patterns: Additional ignore patterns beyond defaults
        use_defaults: Whether to use default ignore patterns
        include_binary: Whether to include binary files
        read_ignore_files: Whether to read .gitignore files
        token_models: List of models to count tokens for (e.g., ['gpt-4o', 'claude-3-5-sonnet-20241022'])
        filter_type: Which files to include ('included', 'removed', 'all')
        content_processor: Optional callback function(relative_path, content) for streaming content
        level: Descend only level directories deep (root is level 0). None means unlimited (default)
        include_dates: Whether to include file creation and modification dates (from git or filesystem)

    Returns:
        root_node: Root of the file tree with aggregated metrics

    Examples:
        # Just build tree with token counting
        root = build_tree("./src", token_models=["gpt-4o"])

        # Build tree and stream content to file
        def write_content(path, content):
            output_file.write(f"### {path}\\n{content}\\n")
        root = build_tree("./src", content_processor=write_content)

        # Build tree with level limit
        root = build_tree("./src", level=2)
    """
    # Set up token counter if models provided
    token_counter = None
    if token_models:
        token_counter = TokenCounter(token_models)

    # Create discoverer
    discoverer = FileDiscoverer(
        root=directory,
        user_patterns=list(ignore_patterns or []),
        use_defaults=use_defaults,
        read_ignore_files=read_ignore_files,
        include_binary=include_binary,
        token_counter=token_counter,
        filter_type=filter_type,
        level=level,
        include_dates=include_dates
    )

    # Discover files and optionally process content in one pass
    files_data = discoverer.discover(content_processor)

    # Build tree from files data
    root = FileSystemTree(files_data).root

    return root


def render_ascii_tree(
    root: FileSystemNode,
    show_stats: bool = True,
    sort_by: str = "name"
) -> str:
    """Render ASCII tree with optional node statistics and sorting.

    Args:
        root: Root node of the tree to render
        show_stats: Whether to show statistics (size, tokens). Default: True
        sort_by: Sort children by 'name' (default), 'size', or any token model name

    Returns:
        ASCII tree representation as string
    """
    plotter = TreePlotter()
    return plotter.plot_ascii(root, show_stats=show_stats, sort_by=sort_by)
