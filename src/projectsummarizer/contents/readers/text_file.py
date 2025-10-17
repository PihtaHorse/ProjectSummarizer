"""Text file content reader."""

from projectsummarizer.contents.readers.base import BaseContentReader


class TextFileReader(BaseContentReader):
    """Reads regular text files with encoding detection."""
    
    def can_read(self, file_path: str, file_data: dict = None) -> bool:
        """Check if this reader handles the file type."""
        # Don't handle binary files - let BinaryFileReader handle them
        if file_data and file_data.get("is_binary", False):
            return False
        # Handle all non-binary files - this is the fallback reader
        return True
    
    def read_content(self, file_path: str, max_size: int, file_data: dict = None) -> str:
        """Extract text content from file, return empty if too large/unreadable."""
        try:
            with open(file_path, "r", encoding='utf-8') as infile:
                content = infile.read()
            return content
        except (OSError, UnicodeDecodeError):
            return ""
