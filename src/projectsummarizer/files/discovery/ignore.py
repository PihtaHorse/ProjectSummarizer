from pathlib import Path
from typing import Iterable, List
from pathspec import PathSpec


class IgnorePatternsHandler:
    """Handles compilation and management of ignore patterns for file discovery."""

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
    ) -> None:
        self.root = Path(root)
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
        if use_defaults:
            pats += list(self.DEFAULT_IGNORE_PATTERNS)
        
        pats += list(user)
        if read_ignore_files:
            pats += self._read_gitignore_patterns_with_prefixes()
        
        return PathSpec.from_lines("gitwildmatch", pats)

    def should_ignore(self, rel_path: str) -> bool:
        """Check if a relative path should be ignored."""
        return self._spec.match_file(rel_path)

    def list_patterns(self) -> List[str]:
        """Get all compiled patterns (for debugging)."""
        return list(self._spec.patterns)
