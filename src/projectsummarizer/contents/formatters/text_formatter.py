"""Streaming text formatter that writes output incrementally without loading all content in memory."""

from typing import TextIO

from projectsummarizer.contents.formatters.base import BaseFormatter


class StreamingTextFormatter(BaseFormatter):
    """Streams formatted file content directly to a file.

    This formatter owns the output file. It opens the file, writes content as it's
    streamed via callbacks, and closes the file.
    """

    def __init__(self, output_path: str, delimiter: str = "```", delimiter_replacement: str = "'''"):
        """Initialize formatter and open output file.

        Args:
            output_path: Path to the output file to create/overwrite
            delimiter: String to use for delimiting file contents
            delimiter_replacement: String to replace delimiter with in content to prevent escape
        """
        self.output_path = output_path
        self.delimiter = delimiter
        self.delimiter_replacement = delimiter_replacement
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

    def write_content(self, relative_path: str, content: str, metadata: dict = None) -> None:
        """Stream a single file's content to output.

        This is designed to be passed as content_processor to build_tree().

        Args:
            relative_path: Relative path of the file
            content: File content
            metadata: Optional dict containing file metadata (size, tokens, created, modified, etc.)
        """
        if content and self.output_file:
            self.file_count += 1

            self.output_file.write(f"## {relative_path}\n\n")

            if metadata:
                created = metadata.get("created")
                modified = metadata.get("modified")

                if created or modified:
                    self.output_file.write("---\n")
                    if created:
                        self.output_file.write(f"created: {created}\n")
                    if modified:
                        self.output_file.write(f"modified: {modified}\n")
                    self.output_file.write("---\n")

            self.output_file.write(f"{self.delimiter}\n")
            safe_content = content.replace(self.delimiter, self.delimiter_replacement)
            self.output_file.write(safe_content)
            self.output_file.write(f"\n{self.delimiter}\n\n")

    def write_tree(self, tree: str) -> None:
        """Prepend the project structure tree to the output.

        Args:
            tree: ASCII tree representation of the project structure
        """
        if not self.output_file:
            raise RuntimeError("Cannot write tree: file is not open")

        self.output_file.flush()

        with open(self.output_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(f"Project Structure:\n{self.delimiter}\n{tree}\n{self.delimiter}\n")
            if current_content:
                f.write("\n" + current_content)
