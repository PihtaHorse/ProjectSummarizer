"""Base formatter for output generation."""

from abc import ABC, abstractmethod
from typing import Dict
from ...files.tree.node import FsNode


class BaseFormatter(ABC):
    """Abstract base for output format generation."""
    
    @abstractmethod
    def format_summary(
        self,
        root: FsNode,
        content_map: Dict[str, str],
        *,
        include_structure: bool = True,
        include_contents: bool = True,
    ) -> str:
        """Generate formatted output from tree and file contents.
        
        Args:
            root: Root node of the file tree
            content_map: Dictionary mapping relative paths to file contents
            include_structure: Whether to include file structure listing
            include_contents: Whether to include file contents
            
        Returns:
            Formatted output string
        """
        pass
