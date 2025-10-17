"""Binary file content reader."""

from projectsummarizer.contents.readers.base import BaseContentReader


class BinaryFileReader(BaseContentReader):
    """Handles binary files by creating a special summary."""
    
    def can_read(self, file_path: str, file_data: dict = None) -> bool:
        """Check if this reader handles the file type."""
        # Handle binary files based on metadata
        if file_data and file_data.get("is_binary", False):
            return True
        return False
    
    def read_content(self, file_path: str, max_size: int, file_data: dict = None) -> str:
        """Create a special summary for binary files."""
        if not file_data:
            return ""
        
        # Create a summary for binary files
        size = file_data.get("size", 0)
        
        return f"binary content ({size} bytes)"
