import os
from pathlib import Path
from typing import Dict, List, Optional
from projectsummarizer.files.discovery.ignore import IgnorePatternsHandler
from projectsummarizer.files.discovery.binary_detector import BinaryDetector


class FileScanner:
    """Discovers files in a directory tree, respecting ignore patterns.

    Uses a centralized IgnorePatternsHandler that handles all ignore logic.
    """

    def __init__(
        self, 
        root: str, 
        *,
        user_patterns: List[str] = None,
        use_defaults: bool = True,
        read_ignore_files: bool = True,
        include_binary: bool = False,
        binary_detector: Optional[BinaryDetector] = None,
        token_counter = None,
        filter_type: str = "included"
    ) -> None:
        self.root = Path(root)
        self.token_counter = token_counter
        self.filter_type = filter_type
        
        # Create the centralized ignore handler
        self.ignore_handler = IgnorePatternsHandler(
            root=root,
            user=user_patterns or [],
            use_defaults=use_defaults,
            read_ignore_files=read_ignore_files,
            include_binary=include_binary,
            binary_detector=binary_detector
        )

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
                full_path = (Path(cur) / fn).as_posix()
                
                # Use centralized ignore logic
                ignore_data = self.ignore_handler.is_ignored(rel, full_path)
                
                # Apply filter logic
                should_include = self._should_include_file(ignore_data["is_ignored"])
                if not should_include:
                    continue

                file_data = self._create_file_data(full_path, ignore_data["is_binary"])
                out[rel] = file_data
        return out
    
    def _should_include_file(self, is_ignored: bool) -> bool:
        """Determine if a file should be included based on filter type."""
        if self.filter_type == "all":
            return True
        elif self.filter_type == "removed":
            return is_ignored
        else:  # "included" (default)
            return not is_ignored
    
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

