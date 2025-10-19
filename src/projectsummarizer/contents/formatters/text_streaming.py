"""Streaming formatter that writes output incrementally without loading all content in memory."""

from typing import TextIO


class StreamingTextFormatter:
    """Streams formatted file content directly to a file.

    This formatter owns the output file. It opens the file, writes content as it's
    streamed via callbacks, and closes the file.
    """

    def __init__(self, output_path: str, delimiter: str = "```"):
        """Initialize formatter and open output file.

        Args:
            output_path: Path to the output file to create/overwrite
            delimiter: String to use for delimiting file contents
        """
        self.output_path = output_path
        self.delimiter = delimiter
        self.file_count = 0
        self.output_file: TextIO = None

    def open(self) -> None:
        """Open the output file for writing."""
        self.output_file = open(self.output_path, "w", encoding="utf-8")
        self.file_count = 0

    def close(self) -> None:
        """Close the output file."""
        if self.output_file:
            self.output_file.close()
            self.output_file = None

    def write_content(self, relative_path: str, content: str) -> None:
        """Stream a single file's content to output.

        This is designed to be passed as content_processor to build_tree().

        Args:
            relative_path: Relative path of the file
            content: File content
        """
        if content and self.output_file:
            self.file_count += 1
            self.output_file.write(f"{relative_path}:\n")
            self.output_file.write(f"{self.delimiter}\n")
            self.output_file.write(content)
            self.output_file.write(f"\n{self.delimiter}\n\n")

    def prepend(self, content: str) -> None:
        """Prepend content to the beginning of the output file.

        This method reads the current file content, prepends the new content,
        and writes everything back. Use this sparingly as it requires
        reading the entire file into memory.

        Args:
            content: Content to prepend to the file
        """
        if not self.output_file:
            raise RuntimeError("Cannot prepend: file is not open")

        # Flush any pending writes
        self.output_file.flush()

        # Read current content
        with open(self.output_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # Write prepended content
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            if current_content:
                f.write('\n' + current_content)

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
