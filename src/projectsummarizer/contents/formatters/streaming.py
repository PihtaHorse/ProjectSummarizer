"""Streaming formatter that writes output incrementally without loading all content in memory."""

from typing import TextIO
from projectsummarizer.files.tree.node import FileSystemNode
from projectsummarizer.contents.formatters.base_streaming import BaseStreamingFormatter


class StreamingTextFormatter(BaseStreamingFormatter):
    """Streams formatted output directly to a file without loading all content in memory.

    This formatter uses a two-pass approach:
    1. First pass: Write the file structure list
    2. Second pass: Stream file contents one at a time via callback

    Memory efficiency: Only one file's content is in memory at a time.
    """

    def __init__(self, delimiter: str = "```"):
        """Initialize with content delimiter.

        Args:
            delimiter: String to use for delimiting file contents
        """
        self.delimiter = delimiter
        self.file_count = 0

    def write_structure(self, root: FileSystemNode, output_file: TextIO) -> None:
        """Write the file structure section to output.

        Args:
            root: Root node of the file tree
            output_file: File handle to write to (must be open)
        """
        output_file.write("Files:\n")
        output_file.write(f"{self.delimiter}\n")

        # Get all file paths from the tree
        file_paths = root.get_file_paths()
        for relative_path in sorted(file_paths):
            output_file.write(f" {relative_path}\n")

        output_file.write(f"{self.delimiter}\n\n")

    def create_content_writer(self, output_file: TextIO):
        """Create a callback function for writing file contents.

        This callback is designed to be passed to FileDiscoverer.discover().

        Args:
            output_file: File handle to write to (must be open)

        Returns:
            Callback function(relative_path, content) that writes formatted content

        Example:
            with open("output.txt", "w") as f:
                formatter = StreamingTextFormatter()
                formatter.write_structure(root, f)
                writer = formatter.create_content_writer(f)
                discoverer.discover(writer)
        """
        def write_content(relative_path: str, content: str) -> None:
            """Callback to write a single file's content."""
            if content:  # Only include non-empty content
                self.file_count += 1
                output_file.write(f"{relative_path}:\n")
                output_file.write(f"{self.delimiter}\n")
                output_file.write(content)
                output_file.write(f"\n{self.delimiter}\n\n")

        return write_content
