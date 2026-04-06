"""Abstract base class for all output formatters."""

from abc import ABC, abstractmethod


class BaseFormatter(ABC):
    """Abstract base for all output formatters.

    Formatters own the output file lifecycle: they open it, stream content
    via write_content() callbacks, prepend the tree structure via write_tree(),
    and close the file.
    """

    file_count: int = 0

    @abstractmethod
    def open(self) -> None:
        """Open the output file for writing."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the output file."""
        ...

    @abstractmethod
    def write_content(self, relative_path: str, content: str, metadata: dict = None) -> None:
        """Stream a single file's content to output.

        Designed to be passed as content_processor to build_tree().

        Args:
            relative_path: Relative path of the file
            content: File content
            metadata: Optional dict with file metadata (size, created, modified, etc.)
        """
        ...

    @abstractmethod
    def write_tree(self, tree: str) -> None:
        """Prepend the project structure tree to the output.

        Called once after all files have been processed.

        Args:
            tree: ASCII tree representation of the project structure
        """
        ...

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
