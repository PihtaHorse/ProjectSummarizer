"""Text file content reader."""

from .base import BaseContentReader


class TextFileReader(BaseContentReader):
    """Reads regular text files with encoding detection."""
    
    def can_read(self, file_path: str) -> bool:
        """Check if this reader handles the file type."""
        # Handle all files - this is the fallback reader
        return True
    
    def read_content(self, file_path: str, max_size: int) -> str:
        """Extract text content from file, return empty if too large/unreadable."""
        try:
            with open(file_path, "r", encoding='utf-8') as infile:
                content = infile.read()
            return content
        except (OSError, UnicodeDecodeError):
            return ""
