"""Text formatter for traditional delimited output."""

from typing import Dict
from .base import BaseFormatter
from ...files.tree.node import FsNode


class TextFormatter(BaseFormatter):
    """Generates the traditional delimited text format (old summarize.py style)."""
    
    def __init__(self, delimiter: str = "```"):
        """Initialize with content delimiter."""
        self.delimiter = delimiter
    
    def format_summary(
        self,
        root: FsNode,
        content_map: Dict[str, str],
        *,
        include_structure: bool = True,
        include_contents: bool = True,
    ) -> str:
        """Output: Files list + delimited file contents."""
        lines = []
        
        if include_structure:
            # Write the project structure
            lines.append("Files:")
            lines.append(self.delimiter)
            
            # Get all file paths from the tree using built-in anytree functionality
            file_paths = root.get_file_paths()
            for relative_path in sorted(file_paths):
                lines.append(f" {relative_path}")
            
            lines.append(self.delimiter)
            lines.append("")  # Empty line
        
        if include_contents:
            # Process and write file contents
            for relative_path in sorted(content_map.keys()):
                content = content_map[relative_path]
                if content:  # Only include non-empty content
                    lines.append(f"{relative_path}:")
                    lines.append(self.delimiter)
                    lines.append(content)
                    lines.append(self.delimiter)
                    lines.append("")  # Empty line
        
        return "\n".join(lines)
