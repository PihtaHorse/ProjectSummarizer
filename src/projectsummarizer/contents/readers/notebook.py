"""Jupyter notebook content reader."""

import nbformat
from .base import BaseContentReader


class NotebookReader(BaseContentReader):
    """Extracts code and markdown cells from Jupyter notebooks."""
    
    def can_read(self, file_path: str) -> bool:
        """Check if this reader handles the file type."""
        return file_path.endswith('.ipynb')
    
    def read_content(self, file_path: str, max_size: int) -> str:
        """Extract text content from notebook, return empty if too large/unreadable."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            content = ""
            for cell in nb.cells:
                if cell.cell_type in ['code', 'markdown']:
                    if cell.source:
                        content += f"# {cell.cell_type.capitalize()} cell\n{cell.source}\n\n"
            return content
        except (OSError, UnicodeDecodeError, Exception):
            return ""
