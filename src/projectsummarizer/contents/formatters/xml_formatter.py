"""XML formatter that outputs content using Anthropic's recommended document structure."""

from typing import TextIO

from projectsummarizer.contents.formatters.base import BaseFormatter


class XMLFormatter(BaseFormatter):
    """Formats project content as XML using Anthropic's recommended structure.

    Output follows the <documents>/<document>/<source>/<document_content> schema,
    which is optimized for LLM consumption. File contents are wrapped in CDATA
    sections to safely handle any special characters.
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
        """Open the output file and write the root opening tag."""
        self.output_file = open(self.output_path, "w", encoding="utf-8")
        self.file_count = 0
        self.output_file.write("<documents>\n")

    def close(self) -> None:
        """Write the root closing tag and close the output file."""
        if self.output_file:
            self.output_file.write("</documents>\n")
            self.output_file.close()
            self.output_file = None

    def write_content(self, relative_path: str, content: str, metadata: dict = None) -> None:
        """Write a single file as an XML document element.

        Args:
            relative_path: Relative path of the file
            content: File content
            metadata: Optional dict containing file metadata (size, tokens, created, modified, etc.)
        """
        if not content or not self.output_file:
            return

        self.file_count += 1
        self.output_file.write(f'<document index="{self.file_count}">\n')
        self.output_file.write(f"<source>{relative_path}</source>\n")

        if metadata:
            created = metadata.get("created")
            modified = metadata.get("modified")
            if created or modified:
                self.output_file.write("<metadata>\n")
                if created:
                    self.output_file.write(f"<created>{created}</created>\n")
                if modified:
                    self.output_file.write(f"<modified>{modified}</modified>\n")
                self.output_file.write("</metadata>\n")

        # CDATA safely handles <, >, & and code delimiters without escaping.
        # Split any literal "]]>" in content across two CDATA sections to avoid
        # prematurely closing the section (e.g. when summarizing this file itself).
        safe_content = content.replace("]]>", "]]]]><![CDATA[>")
        self.output_file.write("<document_content>\n")
        self.output_file.write("<![CDATA[\n")
        self.output_file.write(safe_content)
        self.output_file.write("\n]]>\n")
        self.output_file.write("</document_content>\n")
        self.output_file.write("</document>\n")

    def write_tree(self, tree: str) -> None:
        """Prepend the project structure tree inside a <structure> element.

        Inserts the structure block immediately after the <documents> opening tag.

        Args:
            tree: ASCII tree representation of the project structure
        """
        if not self.output_file:
            raise RuntimeError("Cannot write tree: file is not open")

        self.output_file.flush()

        with open(self.output_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        safe_tree = tree.replace("]]>", "]]]]><![CDATA[>")
        structure_block = "<structure>\n<![CDATA[\n" + safe_tree + "\n]]>\n</structure>\n"

        # Insert after the <documents> opening tag
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("<documents>\n")
            f.write(structure_block)
            # Write everything after the opening <documents> tag
            rest = current_content[len("<documents>\n"):]
            if rest:
                f.write(rest)

        # Reopen in append mode so close() can still write </documents> at the end
        self.output_file.close()
        self.output_file = open(self.output_path, "a", encoding="utf-8")
