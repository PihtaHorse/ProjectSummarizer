"""Base formatter for streaming output generation."""

from abc import ABC, abstractmethod
from typing import TextIO, Callable, Optional
from projectsummarizer.files.tree.node import FileSystemNode


class BaseStreamingFormatter(ABC):
    """Abstract base for streaming output format generation.

    Streaming formatters write output directly to a file handle incrementally,
    without loading all content in memory. This is essential for large projects.

    Subclasses should implement:
    - write_structure(): Write the file/directory structure section
    - create_content_writer(): Return a callback for streaming file contents

    The formatter handles file creation and management internally.
    """

    @abstractmethod
    def write_structure(self, root: FileSystemNode, output_file: TextIO) -> None:
        """Write the file structure section to output.

        Args:
            root: Root node of the file tree
            output_file: File handle to write to (must be open for writing)
        """
        pass

    @abstractmethod
    def create_content_writer(self, output_file: TextIO) -> Callable[[str, str], None]:
        """Create a callback function for writing file contents.

        This callback is designed to be passed to FileDiscoverer.discover().

        Args:
            output_file: File handle to write to (must be open for writing)

        Returns:
            Callback function(relative_path, content) that writes formatted content
        """
        pass

    def format_to_file(
        self,
        output_path: str,
        root: FileSystemNode,
        content_callback_factory: Callable[[Callable[[str, str], None]], None],
        *,
        include_structure: bool = True,
        include_contents: bool = True,
    ) -> None:
        """Format and write output to a file, handling file creation internally.

        This is the main public API for streaming formatters. It manages the file
        lifecycle and coordinates the two-pass writing process.

        Args:
            output_path: Path to the output file to create/overwrite
            root: Root node of the file tree
            content_callback_factory: Function that takes a content writer callback
                                     and uses it to process content (e.g., calls discoverer.discover(callback))
            include_structure: Whether to include file structure listing
            include_contents: Whether to include file contents

        Example:
            formatter = StreamingTextFormatter()

            def process_contents(writer):
                discoverer.discover(writer)

            formatter.format_to_file(
                "output.txt",
                root,
                process_contents,
                include_structure=True,
                include_contents=True
            )
        """
        with open(output_path, "w", encoding="utf-8") as outfile:
            # Write structure section
            if include_structure:
                self.write_structure(root, outfile)

            # Write contents section
            if include_contents:
                content_writer = self.create_content_writer(outfile)
                content_callback_factory(content_writer)
