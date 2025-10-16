"""Base content reader and registry."""

from abc import ABC, abstractmethod
from typing import List
import os


class BaseContentReader(ABC):
    """Abstract base for file content extraction."""
    
    @abstractmethod
    def can_read(self, file_path: str) -> bool:
        """Check if this reader handles the file type."""
        pass
    
    @abstractmethod
    def read_content(self, file_path: str, max_size: int) -> str:
        """Extract text content from file, return empty if too large/unreadable."""
        pass


class ContentReaderRegistry:
    """Manages and selects appropriate reader for files."""
    
    def __init__(self):
        self.readers: List[BaseContentReader] = []
    
    def register(self, reader: BaseContentReader):
        """Add a reader to the registry."""
        self.readers.append(reader)
    
    def read(self, file_path: str, max_size: int = 5*1024*1024) -> str:
        """Try readers in sequence until one successfully reads the file.
        
        Args:
            file_path: Path to the file to read
            max_size: Maximum file size to read (in bytes)
            
        Returns:
            File content as string, empty if file too large or unreadable
        """
        # Check file size first
        try:
            if os.path.getsize(file_path) > max_size:
                return ""
        except OSError as e:
            print(f"Add logging here! Exception: {e}")
            print(f"Some problem with the file {file_path}")
            return ""
        
        # Try readers in sequence until one successfully reads the file
        for reader in self.readers:
            if reader.can_read(file_path):
                content = reader.read_content(file_path, max_size)
                if content:  # If reader successfully read content, stop here
                    return content
        
        # No reader found or all readers returned empty, return empty
        return ""
