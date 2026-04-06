"""Markdown formatter that outputs content as a structured Markdown document."""

from pathlib import Path
from typing import TextIO

from projectsummarizer.contents.formatters.base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Formats project content as a Markdown document.

    Each file is rendered as a level-2 section with a fenced code block.
    The language hint for the code block is inferred from the file extension.
    """

    def __init__(self, output_path: str):
        """Initialize formatter.

        Args:
            output_path: Path to the output file to create/overwrite
        """
        self.output_path = output_path
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
        """Write a single file as a Markdown section with a fenced code block.

        Args:
            relative_path: Relative path of the file
            content: File content
            metadata: Optional dict containing file metadata (size, tokens, created, modified, etc.)
        """
        if not content or not self.output_file:
            return

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
                self.output_file.write("---\n\n")

        language = Path(relative_path).suffix.lstrip(".")
        self.output_file.write(f"```{language}\n")
        self.output_file.write(content)
        self.output_file.write("\n```\n\n")

    def write_tree(self, tree: str) -> None:
        """Prepend the project structure tree as a top-level section.

        Args:
            tree: ASCII tree representation of the project structure
        """
        if not self.output_file:
            raise RuntimeError("Cannot write tree: file is not open")

        self.output_file.flush()

        with open(self.output_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("# Project Structure\n\n")
            f.write("```\n")
            f.write(tree)
            f.write("\n```\n\n")
            if current_content:
                f.write(current_content)
