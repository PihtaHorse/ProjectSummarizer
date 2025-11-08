"""Shared pytest fixtures for tests."""

import pytest
from pathlib import Path
from typing import List


def _create_gitignore(directory: str, patterns: List[str]) -> Path:
    """Create a .gitignore file in the specified directory with given patterns.
    
    Args:
        directory: Path to the directory where .gitignore should be created
        patterns: List of ignore patterns to write to .gitignore
        
    Returns:
        Path to the created .gitignore file
    """
    gitignore_path = Path(directory) / ".gitignore"
    gitignore_path.write_text("\n".join(patterns) + "\n", encoding="utf-8")
    return gitignore_path


def _remove_gitignore(directory: str) -> None:
    """Remove .gitignore file from the specified directory.
    
    Args:
        directory: Path to the directory containing .gitignore
    """
    gitignore_path = Path(directory) / ".gitignore"
    if gitignore_path.exists():
        gitignore_path.unlink()


@pytest.fixture
def test_project_dir():
    """Fixture providing the test project directory path."""
    return Path(__file__).parent / "test_project"


@pytest.fixture
def gitignore_fixture(test_project_dir):
    """Fixture factory for creating .gitignore files with automatic cleanup.
    
    Usage:
        def test_something(gitignore_fixture):
            with gitignore_fixture(["pattern1", "pattern2"]):
                # test code here
            # .gitignore is automatically removed after the context
    """
    def _create_gitignore_context(patterns):
        """Create a context manager that creates and cleans up .gitignore."""
        class GitignoreContext:
            def __init__(self, directory, patterns):
                self.directory = directory
                self.patterns = patterns
            
            def __enter__(self):
                _create_gitignore(str(self.directory), self.patterns)
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                _remove_gitignore(str(self.directory))
        
        return GitignoreContext(test_project_dir, patterns)
    
    return _create_gitignore_context

