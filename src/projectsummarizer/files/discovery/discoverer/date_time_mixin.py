"""Mixin for file date tracking via git history and filesystem timestamps."""

import os
import subprocess
from typing import Optional, Tuple
from datetime import datetime


class DateTimeMixin:
    """Mixin providing file date tracking functionality.

    This mixin adds methods for retrieving file creation and modification dates
    from git history (primary) with filesystem fallback (secondary).

    Requirements:
        The class using this mixin must have:
        - self.root: Path object pointing to the root directory
        - self._is_git_repo_cached: Optional[bool] for caching git repo detection

    Usage:
        class FileDiscoverer(DateTimeMixin):
            def __init__(self, root: str, ...):
                self.root = Path(root)
                self._is_git_repo_cached = None
                ...

    Date Format:
        All dates are returned in YYYY-MM-DD format (e.g., "2025-10-25")
    """

    def _is_git_repo(self) -> bool:
        """Check if the root directory is a git repository.

        Returns:
            True if .git directory exists, False otherwise
        """
        if self._is_git_repo_cached is None:
            self._is_git_repo_cached = (self.root / ".git").exists()
        return self._is_git_repo_cached

    def _get_git_created_date(self, file_path: str) -> Optional[str]:
        """Get the creation date of a file from git history.

        Args:
            file_path: Absolute path to the file

        Returns:
            Date string in YYYY-MM-DD format, or None if not available
        """
        try:
            # Get first commit date for this file
            result = subprocess.run(
                ["git", "log", "--follow", "--format=%aI", "--reverse", "--", file_path],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                # Get first line (earliest commit)
                first_line = result.stdout.strip().split('\n')[0]
                # Parse ISO format to YYYY-MM-DD
                return first_line[:10]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
            pass
        return None

    def _get_git_modified_date(self, file_path: str) -> Optional[str]:
        """Get the last modification date of a file from git history.

        Args:
            file_path: Absolute path to the file

        Returns:
            Date string in YYYY-MM-DD format, or None if not available
        """
        try:
            # Get last commit date for this file
            result = subprocess.run(
                ["git", "log", "-1", "--format=%aI", "--", file_path],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse ISO format to YYYY-MM-DD
                return result.stdout.strip()[:10]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
            pass
        return None

    def _get_filesystem_dates(self, file_path: str) -> Tuple[Optional[str], str]:
        """Get file dates from filesystem as fallback.

        Args:
            file_path: Absolute path to the file

        Returns:
            Tuple of (created_date, modified_date) in YYYY-MM-DD format
            Created date may be None if not available
        """
        try:
            stat_info = os.stat(file_path)

            # Modified date (always available)
            modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d')

            # Created date (platform-dependent)
            created = None
            try:
                # Try st_birthtime (macOS, BSD)
                created = datetime.fromtimestamp(stat_info.st_birthtime).strftime('%Y-%m-%d')
            except AttributeError:
                # Linux doesn't have birthtime, use mtime as fallback
                created = modified

            return (created, modified)
        except OSError:
            # If we can't get filesystem dates, return None
            return (None, None)

    def _get_file_dates(self, full_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get file creation and modification dates.

        Tries git first, falls back to filesystem.

        Args:
            full_path: Absolute path to the file

        Returns:
            Tuple of (created_date, modified_date) in YYYY-MM-DD format
            Either or both may be None if not available
        """
        created = None
        modified = None

        # Try git first if we're in a git repo
        if self._is_git_repo():
            created = self._get_git_created_date(full_path)
            modified = self._get_git_modified_date(full_path)

        # Fallback to filesystem if git didn't provide dates
        if created is None or modified is None:
            fs_created, fs_modified = self._get_filesystem_dates(full_path)
            if created is None:
                created = fs_created
            if modified is None:
                modified = fs_modified

        return (created, modified)
