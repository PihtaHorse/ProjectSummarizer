from pathlib import Path
from typing import Iterable, List, Dict, Set, Optional
from collections import defaultdict
from pathspec import PathSpec
from projectsummarizer.files.discovery.binary_detector import BinaryDetector


class IgnorePatternsHandler:
    """Handles all ignore logic including patterns and binary files.
    
    This class is now the central place for all ignore decisions and tracking.
    It handles both pattern-based ignores and binary file ignores.
    """

    # Default patterns that should always be ignored
    DEFAULT_IGNORE_PATTERNS = [
        ".git",
        ".env",
        ".env.local",
        ".env.*.local",
        "node_modules",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".coverage",
        "*.log",
        ".DS_Store",
        "Thumbs.db",
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        "*~",
    ]

    def __init__(
        self,
        root: str,
        *,
        user: Iterable[str] = (),
        use_defaults: bool = True,
        read_ignore_files: bool = True,
        include_binary: bool = False,
        binary_detector: Optional[BinaryDetector] = None,
    ) -> None:
        self.root = Path(root)
        self.include_binary = include_binary
        self.binary_detector = binary_detector or BinaryDetector()
        
        # Internal tracking - store complete data for all checked files
        self._checked_files: Dict[str, Dict] = {}   # file -> complete ignore_data
        self._pattern_matches: Dict[str, int] = {}  # pattern -> file count
        self._binary_extensions: Set[str] = set()   # extensions of binary files
        
        # Store patterns by origin for tracking
        self._patterns_by_origin: Dict[str, List[str]] = defaultdict(list)
        
        self._spec = self._compile_spec(
            user=user,
            use_defaults=use_defaults,
            read_ignore_files=read_ignore_files,
        )

    def _read_gitignore_patterns_with_prefixes(self) -> List[str]:
        """Read .gitignore patterns with proper directory prefixes."""
        patterns: List[str] = []
        for gi in self.root.rglob(".gitignore"):
            base = gi.parent.relative_to(self.root).as_posix()
            with gi.open("r", encoding="utf-8") as f:
                for raw in f:
                    s = raw.strip()
                    if not s or s.startswith("#"):
                        continue
                    neg = s.startswith("!")
                    body = s[1:] if neg else s
                    # Only add prefix if base is not empty and not the root directory
                    # Both empty string and "." represent the root directory
                    prefixed = f"{base}/{body}" if base and base not in ("", ".") else body
                    patterns.append(("!" + prefixed) if neg else prefixed)
        return patterns

    def _compile_spec(
        self,
        user: Iterable[str],
        *,
        use_defaults: bool,
        read_ignore_files: bool,
    ) -> PathSpec:
        """Compile all patterns into a PathSpec."""
        pats: List[str] = []
        
        # Store patterns by origin for tracking
        if use_defaults:
            self._patterns_by_origin["default"] = list(self.DEFAULT_IGNORE_PATTERNS)
            pats += self._patterns_by_origin["default"]
        
        self._patterns_by_origin["user"] = list(user)
        pats += self._patterns_by_origin["user"]
        
        if read_ignore_files:
            self._patterns_by_origin["gitignore"] = self._read_gitignore_patterns_with_prefixes()
            pats += self._patterns_by_origin["gitignore"]
        
        return PathSpec.from_lines("gitwildmatch", pats)

    def is_ignored(self, rel_path: str, full_path: str) -> Dict:
        """Check if a file should be ignored and return detailed information.
        
        This is the main method that FileScanner will call.
        It handles binary file detection first, then pattern-based ignores.
        Stores complete data for all files (ignored or not).
        
        Args:
            rel_path: Relative path for pattern matching
            full_path: Full path for binary detection
            
        Returns:
            Dictionary with:
            - is_ignored: bool - whether the file should be ignored
            - is_binary: bool - whether the file is binary
            - ignore_reasons: list - reasons for ignoring (if ignored)
        """
        ignore_reasons = []
        matching_patterns = []
        
        # FIRST: Check if file is binary
        is_binary = self.binary_detector.is_binary(full_path)
        if is_binary:
            # Track binary extension
            ext = Path(full_path).suffix.lower()
            if ext:
                self._binary_extensions.add(ext)
            
            # If binary and not including binary files, ignore it
            if not self.include_binary:
                ignore_reasons.append({"type": "binary", "extension": ext})
                
                # Create ignore data for binary files (no pattern matching needed)
                ignore_data = {
                    "is_ignored": True,
                    "is_binary": is_binary,
                    "ignore_reasons": ignore_reasons,
                    "matched_patterns": [],
                    "binary_extension": ext
                }
                
                # Store complete data for all files (ignored or not)
                self._checked_files[rel_path] = ignore_data
                return ignore_data
        
        # SECOND: Only check pattern-based ignores for non-binary files
        if not is_binary:
            for pattern_obj in self._spec.patterns:
                if pattern_obj.match_file(rel_path):
                    pattern_str = str(pattern_obj.pattern)
                    matching_patterns.append(pattern_str)
                    # Track pattern matches
                    self._pattern_matches[pattern_str] = self._pattern_matches.get(pattern_str, 0) + 1
            
            if matching_patterns:
                ignore_reasons.append({"type": "pattern", "patterns": matching_patterns})
        
        # Create complete ignore data
        ignore_data = {
            "is_ignored": len(ignore_reasons) > 0,
            "is_binary": is_binary,
            "ignore_reasons": ignore_reasons,
            "matched_patterns": matching_patterns,
            "binary_extension": Path(full_path).suffix.lower() if is_binary else None
        }
        
        # Store complete data for all files (ignored or not)
        self._checked_files[rel_path] = ignore_data
        
        return ignore_data
    
    def get_pattern_source(self, pattern: str) -> str:
        """Get the source origin of a specific pattern."""
        for origin, patterns in self._patterns_by_origin.items():
            if pattern in patterns:
                return origin
        return "unknown"
    
    def get_binary_extensions(self) -> List[str]:
        """Get extensions that were blocked as binary."""
        return sorted(list(self._binary_extensions))
    
    def get_active_patterns_by_origin(self) -> Dict[str, List[str]]:
        """Get active patterns grouped by their origin."""
        active_patterns_by_origin = defaultdict(list)
        
        for pattern in self._pattern_matches.keys():
            source = self.get_pattern_source(pattern)
            active_patterns_by_origin[source].append(pattern)
        
        # Convert defaultdict to regular dict and remove empty categories
        return {k: v for k, v in active_patterns_by_origin.items() if v}
    
    def get_ignore_stats(self) -> Dict:
        """Get comprehensive ignore statistics."""
        ignored_files = [f for f, data in self._checked_files.items() if data["is_ignored"]]
        return {
            "pattern_matches": dict(self._pattern_matches),
            "binary_extensions": list(self._binary_extensions),
            "ignored_files_count": len(ignored_files),
            "total_checked_files": len(self._checked_files),
            "patterns_by_origin": self.get_active_patterns_by_origin()
        }
    
    def get_checked_files_data(self) -> Dict[str, Dict]:
        """Get complete data for all checked files."""
        return dict(self._checked_files)
    
    def list_patterns(self) -> List[str]:
        """Get all compiled patterns (for debugging)."""
        return [str(p.pattern) for p in self._spec.patterns]
