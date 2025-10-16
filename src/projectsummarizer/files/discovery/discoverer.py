import os
from pathlib import Path
from typing import List
from .ignore import IgnorePatternsHandler


class FileScanner:
    """Discovers files in a directory tree, respecting ignore patterns."""

    def __init__(self, root: str, ignore_handler: IgnorePatternsHandler) -> None:
        self.root = Path(root)
        self.ignore_handler = ignore_handler

    def discover(self) -> List[str]:
        """Return posix-style relative file paths not ignored by spec.
        
        Prunes ignored directories during traversal for efficiency.
        """
        out: List[str] = []
        for cur, dirs, files in os.walk(self.root, topdown=True):
            keep_dirs = []
            for d in dirs:
                rel_dir = (Path(cur) / d).relative_to(self.root).as_posix()
                if not self._dir_is_ignored(rel_dir):
                    keep_dirs.append(d)
            dirs[:] = keep_dirs

            for fn in files:
                rel = (Path(cur) / fn).relative_to(self.root).as_posix()
                if not self.ignore_handler.should_ignore(rel):
                    out.append(rel)
        out.sort()
        return out

    def _dir_is_ignored(self, rel_dir: str) -> bool:
        """Check if a directory should be ignored.
        
        PathSpec typically matches both 'a/b' and 'a/b/' for dir rules.
        """
        return (self.ignore_handler.should_ignore(rel_dir) or 
                self.ignore_handler.should_ignore(rel_dir + "/"))

