import os
from pathlib import Path
from typing import Dict, List
from projectsummarizer.files.discovery.ignore import IgnorePatternsHandler
from projectsummarizer.files.discovery.binary_detector import BinaryDetector


class FileScanner:
    """Discovers files in a directory tree, respecting ignore patterns.

    Optionally excludes binary files based on content detection.
    """

    def __init__(self, root: str, ignore_handler: IgnorePatternsHandler, *, include_binary: bool = False, binary_detector: BinaryDetector | None = None, token_counter = None, filter_type: str = "included") -> None:
        self.root = Path(root)
        self.ignore_handler = ignore_handler
        self.include_binary = bool(include_binary)
        self.binary_detector = binary_detector or BinaryDetector()
        self.token_counter = token_counter
        self.filter_type = filter_type

    def discover(self) -> Dict[str, Dict]:
        """Return posix-style relative file paths with files data based on filter type.
        
        Returns a dictionary mapping relative paths to files data containing:
        - is_binary: bool - whether the file is binary
        - size: int - file size in bytes
        - flags: set - file flags (e.g., 'binary')
        - tokens: dict - token counts (if token_counter provided)
        
        Filter types:
        - "included": files that pass ignore patterns (default)
        - "removed": files that are ignored by patterns
        - "all": all files regardless of ignore patterns
        """
        out: Dict[str, Dict] = {}
        for cur, dirs, files in os.walk(self.root, topdown=True):
            for fn in files:
                rel = (Path(cur) / fn).relative_to(self.root).as_posix()
                
                # Apply filter logic
                if not self._should_include_file(rel):
                    continue
                
                full_path = (Path(cur) / fn).as_posix()
                is_binary = self.binary_detector.is_binary(full_path)
                
                if not self.include_binary and is_binary:
                    continue
                
                file_data = self._create_file_data(full_path, is_binary)
                out[rel] = file_data
        return out
    
    def _should_include_file(self, rel_path: str) -> bool:
        """Determine if a file should be included based on filter type."""
        if self.filter_type == "all":
            return True
        elif self.filter_type == "removed":
            return self.ignore_handler.should_ignore(rel_path)
        else:  # "included" (default)
            return not self.ignore_handler.should_ignore(rel_path)
    
    def _create_file_data(self, full_path: str, is_binary: bool) -> Dict:
        """Create file data dictionary for a given file."""
        # Get file size
        try:
            size = os.path.getsize(full_path)
        except OSError:
            size = 0
        
        # Prepare file data
        file_data = {
            "is_binary": is_binary,
            "size": size,
            "flags": set()
        }
        
        # Add binary flag if present
        if is_binary:
            file_data["flags"].add("binary")
        
        # Add token counts if token_counter is provided
        if self.token_counter:
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tokens = self.token_counter.count_tokens(content)
                file_data["tokens"] = tokens
            except (OSError, UnicodeDecodeError):
                file_data["tokens"] = {}
        else:
            file_data["tokens"] = {}
        
        return file_data

